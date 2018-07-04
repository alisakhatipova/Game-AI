import logging
import sys
import csv
import numpy as np
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from matplotlib.pyplot import cm
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.patheffects as path_effects


logging.basicConfig(level=logging.INFO, stream=sys.stdout,
                    format='%(asctime)s | %(message)s')
logger = logging.getLogger('Logger from Task 2.2')


N_CLUSTERS = 10
ITERATIONS = 1000
USER_STATE_FILE = 'q3dm1-path1.csv'
NEURONS_STATE_FILE = 'neurons.csv'

def get_data(filename):
    with open(filename, 'r') as f:
        reader = csv.reader(f)
        next(reader)
        data = [i for i in reader]
        return np.array(data, dtype=np.float)


def get_activities(user_state_file):
    data = get_data(user_state_file)
    activities = np.full([len(data), 3], -1, dtype=np.float)
    for i in range(len(data)-1):
        activities[i] = data[i+1] - data[i]
    # connect the last and the first coordinates
    activities[len(data)-1] = data[0] - data[-1]
    return activities


def clusterise(data, clusters):
    mapping_array = np.full([len(data), 1], 0, dtype=np.int)

    for i, d in enumerate(data):
        for j, c in enumerate(clusters):
            dist = np.linalg.norm(d-c)
            if dist < np.linalg.norm(d-clusters[mapping_array[0]]):
                logger.debug('point %s (%s) = cluster %s (%s)'
                             % (d, i, c, j))
                mapping_array[i] = j
    return mapping_array

def plot_clusters(data, clusters_map, centers, plot_name='3dplot.png'):
    fig = plt.figure()
    fig.set_size_inches(5.5, 4.5)
    ax = fig.add_subplot(111, projection='3d')
    join_data_cluster = np.append(data, clusters_map, axis=1)

    colors = cm.rainbow(np.linspace(0, 1, len(centers)))
    for i, c in zip(xrange(len(centers)), colors):
        d = join_data_cluster[join_data_cluster[:, -1] == i]
        if d.size > 0:
            t = ax.text(centers[i][0], centers[i][1], centers[i][2], i, color=c)
            t.set_path_effects(
                [path_effects.Stroke(linewidth=3, foreground='black'),
                 path_effects.Normal()])
            ax.scatter(d[:, 0], d[:, 1], d[:, 2],  c=c)

    ax.set_xlim(left=np.min(data[:, 0]), right=np.max(data[:, 0]))
    ax.set_ylim(bottom=np.min(data[:, 1]), top=np.max(data[:, 1]))
    ax.set_zlim(bottom=np.min(data[:, 2]), top=np.max(data[:, 2]))

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    file_path = 'plots/{}'.format(plot_name)
    plt.savefig(file_path, facecolor='w', edgecolor='w',
                papertype=None, format='png', transparent=False,
                pad_inches=0.1, dpi=100)
    # plt.show()


if __name__ == '__main__':
    x = get_data(USER_STATE_FILE)
    neurons = get_data(NEURONS_STATE_FILE)
    activities = get_activities(USER_STATE_FILE)
    kmean = KMeans(n_clusters=N_CLUSTERS,
                   random_state=0,
                   max_iter=ITERATIONS).fit(activities)
    print(kmean.cluster_centers_)
    print(neurons)
    clustered_matrix_a = clusterise(activities, kmean.cluster_centers_)
    print(clustered_matrix_a)
    clustered_matrix_x = clusterise(x, neurons)
    print(clustered_matrix_x)
    plot_clusters(x, clustered_matrix_a, kmean.cluster_centers_, '3d_a_kmean.png')
    plot_clusters(x, clustered_matrix_x, neurons, '3d_x_som.png')
