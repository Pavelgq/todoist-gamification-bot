import matplotlib.pyplot as plt
from io import BytesIO

def generate_stats_chart(stats):
    """
    Генерирует PNG-барчарт статистики наград.
    :param stats: [(имя, единица, число), ...]
    :return: BytesIO — поток PNG-файла.
    """
    if not stats:
        raise ValueError("Статистика пуста — нечего визуализировать!")

    names = [f"{n} ({u})" for n, u, _ in stats]
    values = [t for _, _, t in stats]

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(names, values, color="#6096FD")
    ax.set_title("Заработанные награды")
    ax.set_xlabel("Награда")
    ax.set_ylabel("Количество")
    plt.xticks(rotation=45, ha="right", fontsize=10)
    plt.tight_layout()

    # Добавим подписи над столбцами
    for bar, v in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), str(v),
                ha='center', va='bottom', fontsize=9)

    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)
    return buf
