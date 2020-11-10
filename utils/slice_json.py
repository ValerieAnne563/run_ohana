from osgeo import ogr, osr, gdal

HI_UTM_ZONE = 32601

INTERVAL_MILES = 0.5
INTERVAL_METERS = INTERVAL_MILES * 1600

route_ls_fn = '/Users/valeriehouseman/Desktop/hi_route_ls.json'


def reproject(geom, to_epsg=4326, from_epsg=4326):
    """
    :param geom ogr.Geometry
    """
    source = osr.SpatialReference()
    source.ImportFromEPSG(from_epsg)

    target = osr.SpatialReference()
    target.ImportFromEPSG(to_epsg)

    transform = osr.CoordinateTransformation(source, target)

    geom.Transform(transform)
    return geom


def edge_length(pt_a, pt_b):
    """
    Simple utililty method to calculate the length between two points
    PRE: assume they're in the same CRS

    :param pt_a ogr.Point
    :param pt_b ogr.Point

    returns: length in the units of the CRS
    """
    line = ogr.Geometry(ogr.wkbLineString)
    line.AddPoint(*pt_a)
    line.AddPoint(*pt_b)

    return line.Length()


def measure_along_edge(_pt_a, pt_b, _distance):
    """
    """
    return pt_b


def slice_linestring(linestring, interval_length, debug_limit=None):
    """
    Generator that...
    """
    remainder = 0

    last_interval = linestring.GetPoint(0)
    yield(last_interval)

    for p in range(1, point_count):
        if debug_limit is not None and p > debug_limit:
            break

        next_point = linestring.GetPoint(p)

        edge = edge_length(last_interval, next_point)
        edge = 50

        distance_to = remainder + edge

        while distance_to > interval_length:
            distance_to -= interval_length

            # Calculate interval m along the slope to find the next pt.
            last_interval = measure_along_edge(
                last_interval, next_point, interval_length)
            yield(last_interval)

        remainder = distance_to


if __name__ == '__main__':
    gdal.UseExceptions()

    source_ds = ogr.Open(route_ls_fn)
    assert source_ds is not None

    f = source_ds.GetLayer().GetFeature(0)
    g = f.GetGeometryRef()
    route = reproject(g, to_epsg=HI_UTM_ZONE)

    point_count = route.GetPointCount()
    print('%.02fm route with %d points' % (route.Length(), point_count))

    slices = slice_linestring(route, interval_length=INTERVAL_METERS)
    for i, tup in enumerate(slices):
        point = ogr.Geometry(ogr.wkbPoint)
        point.AddPoint(*tup)

        s = reproject(point, from_epsg=HI_UTM_ZONE)#.GetPoint(0)

        print(i * INTERVAL_MILES, s.GetX(), s.GetY())
