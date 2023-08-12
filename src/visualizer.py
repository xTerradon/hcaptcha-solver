from matplotlib import pyplot as plt
import numpy as np

def plot_captcha_info(info, figsize=(4,10), threshold=100):
    fig, ax1 = plt.subplots()

    fig.set_figheight(figsize[0])
    fig.set_figwidth(figsize[1])

    info = info.sort_values(["solved","total"])

    ax1.axvline(threshold, color="red", label="goal")
    ax1.barh(info.index, info.total, label="captured", color="darkgray")
    ax1.barh(info.index, info.solved, label="solved", color="blue")

    ax1.set_xlabel("# Images")
    ax1.set_xlim(0,threshold*10)

    ax1.legend(loc="lower right")
    ax1.set_title("Available Images per Captcha Type")


def plot_model_accuracy(info, figsize=(4,10)):
    fig, ax1 = plt.subplots()

    fig.set_figheight(figsize[0])
    fig.set_figwidth(figsize[1])

    accuracy_columns = [col for col in info.columns if "accuracy" in col]
    best_accuracy = info[accuracy_columns].max(axis=0)

    info = info.sort_values(accuracy_columns[np.argmax(best_accuracy)], ascending=False)

    ax1.axhline(95, color="red", label="goal", linestyle=":", alpha=0.8)

    if len(accuracy_columns) == 1:
        ax1.bar(info.index, info[accuracy_columns[0]]*100.0, label=accuracy_columns[0].replace("accuracy","").replace("_","_"), color="green", alpha=0.8)
    else:
        for accuracy_column in accuracy_columns:
            ax1.plot(info.index, info[accuracy_column]*100.0, label=accuracy_column.replace("accuracy","").replace("_","_"))

    ax1.set_ylim(50,100)
    ax1.set_ylabel("Labeling Accuracy [%]")
    ax1.legend()


    ax1.legend(loc="lower right")
    ax1.set_title("Labeling Accuracy per Captcha Type")
