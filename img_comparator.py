from copy import deepcopy as copy

import numpy as np


def get_best_indexes(demo_predictions, captcha_predictions):
    mean_demo_predictions = np.array(np.mean(demo_predictions, axis=0), dtype=int)

    relevant_categories = copy(mean_demo_predictions).argsort()[-10:]
    ##print("DEMO PREDICTIONS", np.array([model.config.id2label[b] for b in relevant_categories]))

    diffs = np.array([get_absolute_diff(captcha_predictions[i], mean_demo_predictions) for i in range(len(captcha_predictions))])

    print(diffs.argsort().reshape((3,3)))
    print((diffs < diffs.mean()).reshape((3,3)))

    return diffs


def get_absolute_diff(arr, comp, top_indexes = 0):
    if top_indexes == 0:
        return np.sum(np.abs(arr-comp))
    else:
        best_indexes = np.argsort(comp)[-top_indexes:]
        print(best_indexes)
        return np.sum(np.abs(arr[best_indexes]-comp[best_indexes]))

if __name__ == "__main__":
    arr1 = np.array([[100,8,50],[80,20,30]])
    arr2 = np.array([90,15,40])
    arr3 = np.array([15,90,40])

    mdp = get_best_indexes(arr1, [])
    print(mdp)
    d1 = get_absoulte_diff(arr2, mdp)
    print(d1)
    d2 = get_absoulte_diff(arr3, mdp)
    print(d2)

    d3 = get_absoulte_diff(arr2, mdp, 2)
    print(d3)
    d4 = get_absoulte_diff(arr3, mdp, 2)
    print(d4)


