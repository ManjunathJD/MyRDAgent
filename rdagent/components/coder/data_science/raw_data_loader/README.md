# Raw Data Loader Component

This component is part of the CoSTEER system within the RD-Agent project and is responsible for loading raw data in the context of data science experiments.

## Purpose

The Raw Data Loader component is designed to:

1.  **Load Raw Data:** Handle the process of loading raw datasets into a format that can be used by other components of the data science workflow.
2.  **Data Preprocessing:** Perform any necessary preprocessing steps on the raw data, such as cleaning, formatting, and transformation.
3.  **Integration:** Integrate with the overall data science experiment pipeline, ensuring that data is loaded and available at the appropriate stages.

## Integration with CoSTEER

### Subworkspace

*   The subworkspace used by this component is the main experiment workspace, which is defined in `RD-Agent/rdagent/scenarios/data_science/experiment/experiment.py`.

### Evolving Strategy (implement\_one\_task())

When implementing one task within the evolving strategy, the Raw Data Loader interacts with the following:

1.  **xxxTask (in exp.py):**
    *   **spec:** Specifies the configuration and requirements for loading the raw data.
    *   **description:** Provides a textual description of the data loading task, including any specific requirements or considerations.

### Evaluator

The evaluation of the Raw Data Loader component involves:

1.  **queried\_knowledge:** Leveraging shared knowledge resources to determine the correct data to be loaded.
2.  **eval\_test scripts:** Utilizing evaluation scripts to test and validate the data loading process.