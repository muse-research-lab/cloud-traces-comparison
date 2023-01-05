from typing import List

import matplotlib.pyplot as plt

from gtd.experimentation import Result


def plot_single_report(
    result: Result,
    experiment_name: str,
    metric: str,
    threshold: float,
    normalization: bool,
    conf_matrix: List[List[float]],
    accuracy: float,
    precision: float,
    recall: float,
    colors: List[str],
    path: str,
) -> None:

    baseline_task_uid = result.baseline_task.uid
    baseline_task_data = result.baseline_task.data
    comparison_len = result.baseline_task.data.shape[0]

    min_val = baseline_task_data["avg_cpu_usage"].min()
    max_val = baseline_task_data["avg_cpu_usage"].max()

    dists = [task.dist for task in result.compared_tasks]
    compared_tasks_uids = [task.uid for task in result.compared_tasks]

    fig = plt.figure(figsize=(13, 17), constrained_layout=True)

    gs = fig.add_gridspec(6, 6)

    # Baseline task
    ax1 = fig.add_subplot(gs[0:2, 0:4])

    ax1.plot(baseline_task_data.index, baseline_task_data["avg_cpu_usage"])
    ax1.set_xlabel("Time")
    ax1.set_ylabel("Average CPU usage (%)")

    ax1.set_title("Baseline Task Time Series Data")

    # Metadata
    ax2 = fig.add_subplot(gs[0:2, 4:6])
    ax2.axis("off")

    ax2.text(
        0,
        1,
        f"Experiment {experiment_name}",
        fontdict={
            "weight": "black",
        },
    )
    ax2.text(0, 0.9, f"Baseline Task: {baseline_task_uid}")
    ax2.text(0, 0.825, f"  - {comparison_len} samples")
    ax2.text(0, 0.775, f"  - Values range: {min_val:.5f} - {max_val:.5f}")
    ax2.text(0, 0.675, f"Metric: {metric.capitalize()}")
    ax2.text(0, 0.575, f"Threshold: {threshold:.8f}")
    ax2.text(0, 0.475, f"Normalized Data: {normalization}")

    # Distance Barplot
    ax3 = fig.add_subplot(gs[2:4, 0:2])

    ax3.barh(compared_tasks_uids, dists, align="center", color=colors)
    ax3.tick_params(axis="y", direction="inout", pad=-150)
    ax3.set_xlabel("Distance")
    ax3.set_title("Distances")

    """# Confusion Matrix
    ax4 = fig.add_subplot(gs[4:6, 0:2])

    ax4.matshow(conf_matrix, cmap=plt.cm.Blues, alpha=0.3)
    for i in range(2):
        for j in range(2):
            ax4.text(
                x=j,
                y=i,
                s=conf_matrix[i][j],
                va="center",
                ha="center",
                size="large",
            )

    ticklabels = ["Match", "No-Match"]
    ax4.tick_params(axis="y", labelrotation=90)
    ax4.set_xticks([0, 1], ticklabels)
    ax4.set_yticks([0, 1], ticklabels)

    ax4.set_xlabel("Predictions")
    ax4.set_ylabel("Actuals")
    ax4.set_title("Confusion Matrix")

    # Performance Metrics
    ax5 = fig.add_subplot(gs[6:8, 0:2])

    ax5.bar(
        ["accuracy", "precision", "recall"],
        [accuracy, precision, recall],
        align="center",
        color=["C0", "C1", "C2"],
    )
    ax5.set_ylabel("Percentage (%)")
    ax5.set_title("Performance Metrics")"""

    # Compared tasks
    i = 0
    for task in result.compared_tasks:
        if i == 8:
            break

        if i % 2 == 0:
            ax = fig.add_subplot(gs[i // 2 + 2, 2:4])
        else:
            ax = fig.add_subplot(gs[i // 2 + 2, 4:6])

        ax.plot(task.data.index, task.data["avg_cpu_usage"])

        ax.tick_params(
            left=False,
            right=False,
            labelleft=False,
            labelbottom=False,
            bottom=False,
        )

        ax.set_title(f"Task {task.uid}")

        i = i + 1

    fig.savefig(f"{path}report.png", dpi=600)

    plt.close()


def plot_baseline(
    result: Result,
    path: str,
) -> None:

    baseline_task_uid = result.baseline_task.uid
    baseline_task_data = result.baseline_task.data

    fig, ax = plt.subplots(figsize=(10, 6), constrained_layout=True)

    # Baseline task

    ax.plot(baseline_task_data.index, baseline_task_data["avg_cpu_usage"])
    ax.set_xlabel("Time")
    ax.set_ylabel("Average CPU usage (%)")

    ax.set_title(f"Baseline Task: {baseline_task_uid}")

    fig.savefig(f"{path}baseline.png", dpi=600)

    plt.close()


def plot_dists(
    result: Result,
    colors: List[str],
    path: str,
) -> None:

    dists = [task.dist for task in result.compared_tasks]
    compared_tasks_uids = [task.uid for task in result.compared_tasks]

    fig = plt.figure(figsize=(13, 17), constrained_layout=True)

    # Distance Barplot
    fig, ax = plt.subplots(figsize=(10, 6), constrained_layout=True)

    ax.barh(compared_tasks_uids, dists, align="center", color=colors)
    ax.tick_params(axis="y", direction="inout", pad=-150)
    ax.set_xlabel("Distance")
    ax.set_title("Distances")

    fig.savefig(f"{path}dists.png", dpi=600)

    plt.close()


def create_metadata(
    result: Result,
    metric: str,
    threshold: float,
    normalization: bool,
    path: str,
) -> None:

    baseline_task_uid = result.baseline_task.uid
    baseline_task_data = result.baseline_task.data
    comparison_len = result.baseline_task.data.shape[0]

    min_val = baseline_task_data["avg_cpu_usage"].min()
    max_val = baseline_task_data["avg_cpu_usage"].max()

    f = open(f"{path}metadata.txt", "w")

    f.write(f"Baseline Task: {baseline_task_uid}\n")
    f.write(f"  - {comparison_len} samples\n")
    f.write(f"  - Values range: {min_val:.5f} - {max_val:.5f}\n")
    f.write(f"Metric: {metric.capitalize()}\n")
    f.write(f"Threshold: {threshold:.8f}\n")
    f.write(f"Normalized Data: {normalization}\n")

    f.close()


def plot_single_report_spectrum(
    result: Result,
    experiment_name: str,
    metric: str,
    threshold: float,
    normalization: bool,
    conf_matrix: List[List[float]],
    accuracy: float,
    precision: float,
    recall: float,
    colors: List[str],
    path: str,
) -> None:

    baseline_task_uid = result.baseline_task.uid
    baseline_task_data = result.baseline_task.data
    comparison_len = result.baseline_task.data.shape[0]

    min_val = baseline_task_data["avg_cpu_usage"].min()
    max_val = baseline_task_data["avg_cpu_usage"].max()

    dists = [task.dist for task in result.compared_tasks]
    compared_tasks_uids = [task.uid for task in result.compared_tasks]

    fig = plt.figure(figsize=(13, 17), constrained_layout=True)

    gs = fig.add_gridspec(6, 6)

    # Baseline task
    ax1 = fig.add_subplot(gs[0:2, 0:4])

    Fs = 1 / (5 * 60)
    NFFT = min(baseline_task_data.shape[0], 72)
    noverlap = round(NFFT / 2)

    ax1.specgram(
        baseline_task_data["avg_cpu_usage"],
        NFFT=NFFT,
        Fs=Fs,
        noverlap=noverlap,
        cmap="RdYlGn_r",
    )
    ax1.set_xlabel("Time")
    ax1.set_ylabel("Frequency")

    ax1.set_title("Baseline Task Spectrum Data")

    # Metadata
    ax2 = fig.add_subplot(gs[0:2, 4:6])
    ax2.axis("off")

    ax2.text(
        0,
        1,
        f"Experiment {experiment_name}",
        fontdict={
            "weight": "black",
        },
    )
    ax2.text(0, 0.9, f"Baseline Task: {baseline_task_uid}")
    ax2.text(0, 0.825, f"  - {comparison_len} samples")
    ax2.text(0, 0.775, f"  - Values range: {min_val:.5f} - {max_val:.5f}")
    ax2.text(0, 0.675, f"Metric: {metric.capitalize()}")
    ax2.text(0, 0.575, f"Threshold: {threshold:.8f}")
    ax2.text(0, 0.475, f"Normalized Data: {normalization}")

    # Distance Barplot
    ax3 = fig.add_subplot(gs[2:4, 0:2])

    ax3.barh(compared_tasks_uids, dists, align="center", color=colors)
    ax3.tick_params(axis="y", direction="inout", pad=-150)
    ax3.set_xlabel("Distance")
    ax3.set_title("Distances")

    """# Confusion Matrix
    ax4 = fig.add_subplot(gs[4:6, 0:2])

    ax4.matshow(conf_matrix, cmap=plt.cm.Blues, alpha=0.3)
    for i in range(2):
        for j in range(2):
            ax4.text(
                x=j,
                y=i,
                s=conf_matrix[i][j],
                va="center",
                ha="center",
                size="large",
            )

    ticklabels = ["Match", "No-Match"]
    ax4.tick_params(axis="y", labelrotation=90)
    ax4.set_xticks([0, 1], ticklabels)
    ax4.set_yticks([0, 1], ticklabels)

    ax4.set_xlabel("Predictions")
    ax4.set_ylabel("Actuals")
    ax4.set_title("Confusion Matrix")

    # Performance Metrics
    ax5 = fig.add_subplot(gs[6:8, 0:2])

    ax5.bar(
        ["accuracy", "precision", "recall"],
        [accuracy, precision, recall],
        align="center",
        color=["C0", "C1", "C2"],
    )
    ax5.set_ylabel("Percentage (%)")
    ax5.set_title("Performance Metrics")"""

    # Compared tasks
    i = 0
    for task in result.compared_tasks:
        if i == 8:
            break

        if i % 2 == 0:
            ax = fig.add_subplot(gs[i // 2 + 2, 2:4])
        else:
            ax = fig.add_subplot(gs[i // 2 + 2, 4:6])

        Fs = 1 / (5 * 60)
        NFFT = min(baseline_task_data.shape[0], 72)
        noverlap = round(NFFT / 2)

        ax.specgram(
            task.data["avg_cpu_usage"],
            NFFT=NFFT,
            Fs=Fs,
            noverlap=noverlap,
            cmap="RdYlGn_r",
        )

        ax.tick_params(
            left=False,
            right=False,
            labelleft=False,
            labelbottom=False,
            bottom=False,
        )

        ax.set_title(f"Task {task.uid}")

        i = i + 1

    fig.savefig(f"{path}report.png", dpi=600)

    plt.close()


def plot_baseline_spectrum(
    result: Result,
    path: str,
) -> None:

    baseline_task_uid = result.baseline_task.uid
    baseline_task_data = result.baseline_task.data

    fig, ax = plt.subplots(figsize=(10, 6), constrained_layout=True)

    Fs = 1 / (5 * 60)
    NFFT = min(baseline_task_data.shape[0], 72)
    noverlap = round(NFFT / 2)

    ax.specgram(
        baseline_task_data["avg_cpu_usage"],
        NFFT=NFFT,
        Fs=Fs,
        noverlap=noverlap,
        cmap="RdYlGn_r",
    )
    ax.set_xlabel("Time")
    ax.set_ylabel("Frequency")

    ax.set_title(f"Baseline Task: {baseline_task_uid}")

    fig.savefig(f"{path}baseline.png", dpi=600)

    plt.close()
