from matplotlib import pyplot as plt

def plot_captcha_info(info, threshold=50):
    fig, ax1 = plt.subplots()

    fig.set_figheight(4)
    fig.set_figwidth(10)

    info = info.sort_values("total")

    if "accuracy" in info.columns:
        ax2 = ax1.twiny()
        info = info.sort_values("accuracy")
        ax1.barh(info.index, info.solved, label="solved", color="blue", alpha=0.2)
        ax2.scatter(info.accuracy, info.index, label="accuracy", color="green", marker="D")
        ax2.set_xlim(0.5,1)
        ax2.set_xlabel("Accuracy")
        ax2.legend()

    else:
        ax1.axvline(threshold, color="red", label="goal")
        ax1.barh(info.index, info.total, label="captured", color="darkgray")
        ax1.barh(info.index, info.solved, label="solved", color="blue")
    ax1.set_xlabel("# images")
    ax1.set_xlim(0,200)

    ax1.legend(loc="lower right")
    ax1.set_title("Captcha per Type")
