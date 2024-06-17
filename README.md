# sample-python-libs

This repository contains a simple Python library that simplifies the process of writing custom events to a Fabric Table through Fabric Notebooks.

It also showcases pipelines that illustrate diverse methods and tools for packaging and distributing Python libraries. For more details, refer to the [wheel-generation](./docs/wheel-generation.md) document.

## Library Description

The `EventsPersistenceManager` class in the `events_persistence_manager.py` file is designed to manage the persistence of event data into Delta tables using Apache Spark. It provides functionality to save custom events, missing data events, and exception events, with the ability to decorate these events with additional context before saving.

The `Context` class, referenced from `custom_events_lib.context`, is used to encapsulate additional information that can be associated with events, such as the activity name, user name, and environment details. This context is used to enrich the event data before it is persisted.

The `EventsPersistenceManager` is designed to be used in applications that require the persistence of event data into Delta tables with rich context information. It abstracts the complexities of schema validation and context decoration, providing a simple interface for saving various types of events.

## How to use it?

1. Create a wheel by following the instructions in the [wheel-generation](./docs/wheel-generation.md) document or run the following command:

```bash
python -m build
```

2. [Create a Fabric environment](https://learn.microsoft.com/en-us/fabric/data-engineering/create-and-use-environment#create-an-environment) and upload the custom library as explained [here](https://learn.microsoft.com/en-us/fabric/data-engineering/environment-manage-library#custom-libraries).

3. Create a new notebook or use the provided example notebook [custom_events_notebook.ipynb](custom_events_notebook.ipynb) that demonstrates how to use the library. You can use the [import notebook](https://learn.microsoft.com/en-us/fabric/data-engineering/how-to-use-notebook#import-existing-notebooks) functionality.

4. Attach previously created environment following [this documentation](https://learn.microsoft.com/en-us/fabric/data-engineering/create-and-use-environment#attach-an-environment).

5. The example notebook writes data to a Delta table, so make sure you choose the correct lakehouse and [set it as the default](https://learn.microsoft.com/en-us/fabric/data-engineering/lakehouse-notebook-explore#switch-lakehouses-and-set-a-default).

6. Explore your data by checking your custom events table and customize a chart according to your needs.