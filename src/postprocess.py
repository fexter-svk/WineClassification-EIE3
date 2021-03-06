import itertools
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, precision_score, recall_score, f1_score
import os


def calculate_MAD(y_test, y_pred):
    s = 0
    for i in range(len(y_test)):
        s+=abs(y_test[i]-y_pred[i])
    return s/len(y_test)

# This function calculates the recall, precision scores and saves it into a file
def calculate_scores(y_test, y_pred, name,model, fold = None):
    with open("{}/{}/{}/{}_{}/scores_{}.txt".format(model,"logs",name, name,fold, name), "w") as text_file:
        # It might happen that a quality can be not represented at all in a test, training, val set
        # Hence check for that case because the classifier might not have seen that quality at all
        classes_pred = [str(i) for i in np.unique(y_pred)]
        classes_test = [str(i) for i in np.unique(y_test)]

        classes = None
        if len(classes_pred)>len(classes_test):
            classes = classes_pred
        else:
            classes = classes_test

        p_score =  precision_score(y_test, y_pred, average=None)
        text_file.write("Labels:\n{}\n".format(classes))
        text_file.write("Precision scores:\n{}\n".format(p_score))

        r_score =  recall_score(y_test, y_pred, average=None)
        text_file.write("Labels:\n{}\n".format(classes))
        text_file.write("Recall scores:\n{}".format(r_score))

        f1 =  f1_score(y_test, y_pred, average=None)
        text_file.write("Labels:\n{}\n".format(classes))
        text_file.write("F1 scores:\n{}".format(f1))

# This function calculates the confusion matrix and visualizes it
def plot_confusion_matrix(y_test, y_pred, name, model,
                          normalize=False,
                          title='Confusion matrix',
                          cmap=plt.cm.Blues,
                          fold = None):

    # Compute confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    np.set_printoptions(precision=2)

    classes_pred = [str(i) for i in np.unique(y_pred)]
    classes_test = [str(i) for i in np.unique(y_test)]

    classes = None
    if len(classes_pred)>len(classes_test):
        classes = classes_pred
    else:
        classes = classes_test
    # In case the confusion matrix should be normalized
    if normalize:
        t = cm.sum(axis=1)[:, np.newaxis]
        for i in t:
            if i[0] == 0:
                i[0] = 1
        cm = cm.astype('float') / t

    plt.figure()
    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=45)
    plt.yticks(tick_marks, classes)


    thresh = cm.max() / 2.0
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, np.around(cm[i, j],2),
                 horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black")

    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')

    if not os.path.isdir("{}/{}/{}/{}_{}".format(model,"logs",name, name,fold)):
        os.makedirs("{}/{}/{}/{}_{}".format(model,"logs",name, name,fold))

    if normalize:
        plt.savefig("{}/{}/{}/{}_{}/cm_n_{}.png".format(model,"logs",name, name,fold, name))
    else:
        plt.savefig("{}/{}/{}/{}_{}/cm_{}.png".format(model,"logs",name, name,fold, name))
    plt.close()
