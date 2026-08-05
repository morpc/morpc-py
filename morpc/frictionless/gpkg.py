# morpc-py/morpc/frictionless/gpkg.py

"""Frictionless support for GeoPackage (.gpkg) resources.

Frictionless has no built-in parser for spatial formats, so this module registers a
"gpkg" resource type that bypasses Frictionless's row-streaming engine and validates
GeoPackage layers directly via geopandas/pyogrio -- the same approach
morpc.rest_api.ArcGISResource uses for the "arcgis" type (see morpc/rest_api/rest_api.py).

A single GeoPackage file may contain multiple layers. Each layer is described by its
own Frictionless Resource, all sharing the same `path` but carrying a different
GpkgControl.layer. Schemas are never generated from the data here -- they must be
hand-written and are validated against, consistent with how every other morpc format
is handled in this module.
"""

import logging

import attrs
import frictionless
from frictionless.dialect import Control

logger = logging.getLogger(__name__)


@attrs.define(kw_only=True, repr=False)
class GpkgControl(Control):
    """Control identifying which layer of a GeoPackage file a Resource describes."""

    type = "gpkg"

    layer: str | None = None

    metadata_profile_patch = {
        "properties": {
            "layer": {"type": "string"},
        }
    }


class GpkgPlugin(frictionless.Plugin):
    """Frictionless plugin that registers GpkgResource/GpkgControl for type='gpkg'."""

    def select_resource_class(self, type=None, *, datatype=None):
        if type == "gpkg":
            return GpkgResource

    def select_control_class(self, type=None):
        if type == "gpkg":
            return GpkgControl


frictionless.system.register("gpkg", GpkgPlugin())


@attrs.define
class GpkgValidationReport:
    """Minimal stand-in for frictionless.Report, returned by GpkgResource.validate().

    Only exposes what morpc.frictionless.validate_resource() relies on: a `valid`
    flag and a human-readable string representation of the errors.
    """

    valid: bool
    errors: list[str] = attrs.Factory(list)

    def __str__(self):
        return "Valid" if self.valid else "\n".join(self.errors)


class GpkgResource(frictionless.Resource):
    """A Frictionless Resource describing a single layer of a GeoPackage file."""

    type = "gpkg"

    def to_geodataframe(self):
        """Load this resource's layer as a GeoDataFrame."""
        import geopandas as gpd

        control = GpkgControl.from_dialect(self.dialect)
        if control.layer is None:
            logger.error("GpkgControl.layer is not set on this resource's dialect; cannot determine which layer to read.")
            raise RuntimeError

        return gpd.read_file(self.path, layer=control.layer, engine="pyogrio")

    def validate(
        self,
        *,
        checkNullGeometry: bool = True,
        checkDuplicateGeometry: bool = True,
        checkValidGeometry: bool = True,
        expectedCRS: str | None = None,
        expectedGeometryType: str | None = None,
        expectedBounds: tuple[float, float, float, float] | None = None,
    ) -> GpkgValidationReport:
        """Validate this layer against its schema and, optionally, spatial expectations.

        Schema conformance (missing fields, field types) is always checked against
        self.schema, which must already be set (schemas are hand-written, never
        inferred from the data -- see morpc.frictionless.create_gpkgresource()).

        The geometry-integrity checks (null/duplicate/invalid geometry) run by default
        since they require no external input. The CRS, geometry-type, and extent checks
        are skipped unless their corresponding "expected" value is supplied, since this
        module has no way to infer the correct CRS, geometry type, or extent for an
        arbitrary dataset.

        Parameters
        ----------
        checkNullGeometry : bool
            If True (default), flag rows with null or empty geometry.
        checkDuplicateGeometry : bool
            If True (default), flag rows with duplicate geometry.
        checkValidGeometry : bool
            If True (default), flag rows with invalid geometry (e.g. self-intersections).
        expectedCRS : str, optional
            If provided, flag a mismatch between this and the layer's CRS.
        expectedGeometryType : str, optional
            If provided (e.g. "Point"), flag rows whose geometry type differs.
        expectedBounds : tuple of float, optional
            If provided as (minx, miny, maxx, maxy), flag rows falling outside these bounds.

        Returns
        -------
        report : GpkgValidationReport
            report.valid is True if no errors were found. report.errors lists each
            problem found.
        """
        from morpc.frictionless.frictionless import cast_field_types

        errors = []
        gdf = self.to_geodataframe()
        geometryColumn = gdf.geometry.name

        if self.schema is not None:
            missingFields = [field.name for field in self.schema.fields if field.name not in gdf.columns]
            if missingFields:
                errors.append(f"Schema field(s) not present in layer '{self.path}': {missingFields}")
            try:
                # Missing fields were already reported above with a clearer message than
                # cast_field_types raises, so skip them here and only check field types.
                cast_field_types(gdf.drop(columns=geometryColumn), self.schema, handleMissingFields="ignore")
            except Exception:
                errors.append("One or more fields could not be cast to the type declared in the schema. See log for details.")

        if checkNullGeometry:
            nullCount = int((gdf.geometry.isna() | gdf.geometry.is_empty).sum())
            if nullCount > 0:
                errors.append(f"{nullCount} row(s) have null or empty geometry.")

        if checkDuplicateGeometry:
            duplicateCount = int(gdf.geometry.duplicated().sum())
            if duplicateCount > 0:
                errors.append(f"{duplicateCount} row(s) have duplicate geometry.")

        if checkValidGeometry:
            invalidMask = gdf.geometry.notna() & ~gdf.geometry.is_empty & ~gdf.geometry.is_valid
            invalidCount = int(invalidMask.sum())
            if invalidCount > 0:
                errors.append(f"{invalidCount} row(s) have invalid geometry (e.g. self-intersections).")

        if expectedCRS is not None:
            from pyproj import CRS as _CRS
            if gdf.crs is None or _CRS(gdf.crs) != _CRS(expectedCRS):
                errors.append(f"Expected CRS '{expectedCRS}' but layer has CRS '{gdf.crs}'.")

        if expectedGeometryType is not None:
            mismatchedTypes = set(gdf.geom_type.dropna().unique()) - {expectedGeometryType}
            if mismatchedTypes:
                errors.append(f"Expected geometry type '{expectedGeometryType}' but found: {sorted(mismatchedTypes)}.")

        if expectedBounds is not None:
            minx, miny, maxx, maxy = expectedBounds
            bounds = gdf.geometry.bounds
            outOfBounds = gdf[
                (bounds["minx"] < minx) | (bounds["miny"] < miny) | (bounds["maxx"] > maxx) | (bounds["maxy"] > maxy)
            ]
            if len(outOfBounds) > 0:
                errors.append(f"{len(outOfBounds)} row(s) fall outside expected bounds {expectedBounds}.")

        return GpkgValidationReport(valid=(len(errors) == 0), errors=errors)


def create_gpkgresource(
    dataPath,
    layerNames,
    schemaPaths=None,
    title=None,
    name=None,
    description=None,
    sources=None,
    resourceDir=None,
    resProfile=None,
    resMediaType=None,
    computeHash=True,
    computeBytes=True,
    writeResource=False,
    validate=False,
    cache=None,
    hashAlgorithm="md5",
):
    """Create one Frictionless Resource per layer of a GeoPackage file.

    Schemas are hand-written and validated against -- they are never inferred from the
    data. This mirrors morpc.frictionless.create_resource(), but produces one Resource
    per layer since a single GeoPackage file may contain several layers/tables.

    Parameters
    ----------
    dataPath : str
        The path to the GeoPackage file, as you want it to appear in each resource
        file. See create_resource() for path conventions.
    layerNames : str or list of str
        The name(s) of the layer(s) to describe, one Resource per layer.
    schemaPaths : str or list of str, optional
        Path to a single hand-written schema file to apply to every layer, or a list
        of schema paths matching layerNames one-to-one. If omitted, no schema is
        attached (equivalent to create_resource(ignoreSchema=True)).
    title, description, sources, resProfile, resMediaType, computeHash, computeBytes,
    writeResource, validate, cache, hashAlgorithm
        Passed through to create_resource() for every layer. See create_resource()
        for details.
    name : str, optional
        Base name for the resources. Each layer's resource name is "{name}-{layer}"
        (or derived from the data file name if unspecified), since resource names
        must be unique within a package.
    resourceDir : str, optional
        Directory to write each layer's resource file to. Each file is named
        "{dataFileName}-{layerName}.resource.yaml". Required if writeResource is True.

    Returns
    -------
    resources : list of frictionless.resources.table.TableResource
        One Resource per layer, in the same order as layerNames.
    """
    import os
    import re

    from morpc.frictionless.frictionless import create_resource

    if isinstance(layerNames, str):
        layerNames = [layerNames]

    if schemaPaths is None or isinstance(schemaPaths, str):
        schemaPaths = [schemaPaths] * len(layerNames)
    elif len(schemaPaths) != len(layerNames):
        logger.error("schemaPaths must be a single path (applied to all layers) or a list matching the length of layerNames.")
        raise RuntimeError

    dataFileName = os.path.splitext(os.path.basename(dataPath))[0]
    baseName = name if name is not None else re.sub(r"\W+", "-", dataFileName).lower()
    baseTitle = title if title is not None else dataFileName

    resources = []
    for layerName, schemaPath in zip(layerNames, schemaPaths):
        resourcePath = None
        if resourceDir is not None:
            resourcePath = os.path.join(resourceDir, f"{dataFileName}-{layerName}.resource.yaml")

        resource = create_resource(
            dataPath,
            title=f"{baseTitle} - {layerName}",
            name=f"{baseName}-{layerName}",
            description=description,
            sources=sources,
            resourcePath=resourcePath,
            schemaPath=schemaPath,
            ignoreSchema=(schemaPath is None),
            resFormat="gpkg",
            resProfile=resProfile,
            resMediaType=resMediaType,
            computeHash=computeHash,
            computeBytes=computeBytes,
            writeResource=writeResource,
            validate=validate,
            control=GpkgControl(layer=layerName),
            cache=cache,
            hashAlgorithm=hashAlgorithm,
        )
        resources.append(resource)

    return resources
