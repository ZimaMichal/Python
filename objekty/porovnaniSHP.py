import geopandas as gpd

def find_changes(new_shapefile, old_shapefile):
    # Read the shapefiles
    new_data = gpd.read_file(new_shapefile)
    old_data = gpd.read_file(old_shapefile)

    # Find new features
    new_features = new_data[~new_data['IDENT_OBJ'].isin(old_data['IDENT_OBJ'])]

    # Find deleted features
    deleted_features = old_data[~old_data['IDENT_OBJ'].isin(new_data['IDENT_OBJ'])]

    # Write new features to a new shapefile
    if not new_features.empty:
        new_features.to_file("new_features.shp")

    # Write deleted features to a new shapefile
    if not deleted_features.empty:
        deleted_features.to_file("deleted_features.shp")

    print("Shapefiles with changes have been created.")
# Usage
new_shapefile = "C:/Work/objekty/OBJEKTY_2024/vypocty/mosty_2401_lok.shp"
old_shapefile = "C:/Work/objekty/OBJEKTY_2024/vypocty/mosty_2307_lok.shp"
find_changes(new_shapefile, old_shapefile)
