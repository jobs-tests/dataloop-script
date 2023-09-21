import os
import dtlpy as dl
from dataloop_script.constants import project_name, dataset_name
from dataloop_script.helpers import group_annotations_by_item, print_annotations, add_annotations, get_or_create_dataset, get_or_create_project, print_items, query_annotation_with_type, query_item_with_label
from dataloop_script.utils import format_unix_timestamp, load_json, setup_file_paths


def main():
    # Get Current Directory and file paths
    images_folder, annotation_file_path = setup_file_paths()

    # Read annotations from file 
    annotations_dict = load_json(annotation_file_path)

    # Check and log in if the token is expired
    if dl.token_expired():
        dl.login()

    # 2a - Create New Dataset
    project = get_or_create_project(dl.projects, project_name)
    dataset = get_or_create_dataset(project.datasets, dataset_name)

    # 2b - Adding Label
    dataset.add_labels(["1", "2", "3", "top", "bottom"])

    print("Uploading Image and Annotation")
    for img_filename in os.listdir(images_folder):
        img_local_path = os.path.join(images_folder, img_filename)

        # 2c - upload each image in the directory with three images (1.jpg, 2.jpg, 3.jpg)
        # 2d - Add a UTM metadata to an item user metadata - collection time 
        item = dataset.items.upload(
            local_path=img_local_path,
            remote_path="/in_storm",
            overwrite=False,
            item_metadata={"user": {"collected": format_unix_timestamp()}},
        )
        assert isinstance(item, dl.Item)

        annotations = annotations_dict.get(img_filename, [])

        # 2e - Process and upload annotations using the modularized function
        add_annotations(item, annotations)

    # 2f - Creating a query that selects only image items that have been labeled as top
    # and print out the items
    print("\nQuerying and Printing Item Result")
    pages = query_item_with_label(dataset, 'top')
    print_items(pages)

    # 2e - Creating a query that retrieves all point annotations from the dataset 
    # and prints the item name and item id of each item, 
    # and for each item, print for each annotation the annotation id, annotation label, and position of the point (x,y)
    print("\nQuerying and Printing Annotation Result")
    pages = query_annotation_with_type(dataset=dataset, type="point")
    annotations_by_item = group_annotations_by_item(pages)
    print_annotations(annotations_by_item)


if __name__ == "__main__":
    main()
