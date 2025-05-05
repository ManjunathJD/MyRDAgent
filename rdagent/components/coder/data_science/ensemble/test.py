"""
Helper functions for testing the ensemble coder(CoSTEER-based) component.
"""

import sys
from pathlib import Path

try:
    from rdagent.components.coder.data_science.ensemble import EnsembleCoSTEER
    from rdagent.components.coder.data_science.ensemble.exp import EnsembleTask
    from rdagent.scenarios.data_science.experiment.experiment import DSExperiment
    from rdagent.scenarios.data_science.scen import KaggleScen
except ImportError:
    print("Error: Could not import required modules. Please check your environment and dependencies.")
    sys.exit(1)


def load_ensemble_spec():
    spec_path = COMPETITION_PATH / "spec" / "ensemble.md"
    with open(spec_path, "r") as f:
        return f.read()


def develop_one_competition(competition: str, COMPETITION_PATH:Path ):
    # Initialize scenario and coder
    scen = KaggleScen(competition=competition)
    ensemble_coder = EnsembleCoSTEER(scen)
    # Load ensemble specification
    ensemble_spec = load_ensemble_spec()

    # Create the ensemble task with actual data context and specification
    task = EnsembleTask(
        name="EnsembleTask",
        description="""
        Implement ensemble and decision making for model predictions.
        """,
    )

    exp = EnsembleExperiment(pending_tasks_list=[task])

    # Injecting the corresponding specification
    exp.experiment_workspace.inject_files(**{"spec/ensemble.md": ensemble_spec})

    # Develop the experiment
    exp = ensemble_coder.develop(exp)
    return exp


if __name__ == "__main__":
        # Add the competition folder to path
    COMPETITION_PATH = (
        Path(__file__).parent.parent.parent.parent.parent
        / "scenarios"
        / "kaggle"
        / "tpl_ex"
        / "aerial-cactus-identification"
    )
    sys.path.append(str(COMPETITION_PATH))

    EnsembleExperiment = DSExperiment
    develop_one_competition("aerial-cactus-identification", COMPETITION_PATH)

