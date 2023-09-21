import dtlpy as dl
from dtlpy import exceptions
from dtlpy.entities import AnnotationCollection, Item, PagedEntities
from dtlpy.repositories import Datasets, Projects


def get_or_create_project(projects: Projects, project_name: str):
    try:
        return projects.get(project_name)
    except exceptions.NotFound:
        print("Project Name doesn't exist, creating a new one")
        return projects.create(project_name)


def get_or_create_dataset(datasets: Datasets, dataset_name: str):
    try:
        return datasets.get(dataset_name)
    except exceptions.NotFound:
        print("Dataset name doesn't exist, creating a new one")
        return datasets.create(dataset_name)


def create_box_annotation(annotation):
    label_name = str(annotation["label"])
    x1, y1 = annotation["box"][0]["x"], annotation["box"][0]["y"]
    x2, y2 = annotation["box"][1]["x"], annotation["box"][1]["y"]
    top, left = min(y1, y2), min(x1, x2)
    bottom, right = max(y1, y2), max(x1, x2)
    return dl.Box(top=top, left=left, bottom=bottom, right=right, label=label_name)


def create_point_annotation(annotation):
    label_name = str(annotation["label"])
    x, y = annotation["point"]["x"], annotation["point"]["y"]
    return dl.Point(x=x, y=y, label=label_name)


def create_polygon_annotation(annotation):
    label_name = str(annotation["label"])
    polygon_points = annotation["polygon"][0]
    geo = [[point["x"], point["y"]] for point in polygon_points]
    return dl.Polygon(geo=geo, label=label_name)


def create_annotation_definition(annotation):
    annotation_definition = None
    if "box" in annotation:
        annotation_definition = create_box_annotation(annotation)
    elif "point" in annotation:
        annotation_definition = create_point_annotation(annotation)
    elif "polygon" in annotation:
        annotation_definition = create_polygon_annotation(annotation)
    return annotation_definition


def build_annotation(builder: AnnotationCollection, annotation):
    confidence = annotation["confidence"]
    model_info = {"name": "", "confidence": confidence}

    annotation_definition = create_annotation_definition(annotation)

    if annotation_definition:
        builder.add(annotation_definition=annotation_definition, model_info=model_info)


def add_annotations(item: Item, annotations):
    builder = item.annotations.builder()

    for annotation in annotations:
        build_annotation(builder, annotation)

    item.annotations.upload(builder)


def group_annotations_by_item(pages):
    annotations_by_item = {}

    for page in pages:
        for annotation in page:
            item_name = annotation.item.name
            item_id = annotation.item_id
            if (item_name, item_id) not in annotations_by_item:
                annotations_by_item[(item_name, item_id)] = []

            annotations_by_item[(item_name, item_id)].append(
                {
                    "annotation_id": annotation.id,
                    "label": annotation.label,
                    "coordinates": annotation.coordinates,
                }
            )

    return annotations_by_item


def query_annotation_with_type(
    dataset: Datasets, type: str
) -> AnnotationCollection | PagedEntities:
    # Create filters instance with annotation resource
    filters = dl.Filters(resource=dl.FiltersResource.ANNOTATION)
    # Filter example - only point annotations
    filters.add(field="type", values=type)
    return dataset.annotations.list(filters=filters)


def print_annotations(annotations_by_item):
    for (item_name, item_id), annotations in annotations_by_item.items():
        print()
        print(f"Item Name: {item_name}, Item ID: {item_id}")
        for annotation in annotations:
            print(f'  Annotation ID: {annotation["annotation_id"]}')
            print(f'  Annotation Label: {annotation["label"]}')
            print(
                f'  Position : [{annotation["coordinates"]["x"]}, {annotation["coordinates"]["y"]}]'
            )
            print()


def query_item_with_label(dataset: Datasets, label: str) -> PagedEntities:
    filters = dl.Filters()
    filters.add_join(field="label", values=label)
    return dataset.items.list(filters=filters)


def print_items(pages: PagedEntities):
    filtered_items = pages.items

    # Calculate the maximum width for the "Id" column
    max_id_width = max(len(str(item.id)) for item in filtered_items)

    # Print the table header
    print(f"{'Id':<{max_id_width}}\tName")

    # Print the items in a table format
    for item in filtered_items:
        print(f"{item.id:<{max_id_width}}\t{item.name}")
