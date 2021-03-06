import os
import sys
import copy
import numpy as np

from .visualize import visualize
from .linear import LinearRegressionClassifier
from postprocess import plot_confusion_matrix, calculate_scores, calculate_MAD

# Separete the labels from the features
def separete_data(data):
    features = np.array(copy.deepcopy([x[:-1] for x in data]), dtype=np.float64)
    labels = np.array(copy.deepcopy([x[-1] for x in data]), dtype=np.int32)
    return (features, labels)

# This function performs training for the specific network and performs n_fold cross validation
def n_fold(model, n_folds = 10, save = True, test = False):
    LEARNING_RATE = float(model["LEARNING_RATE"])
    LOSS = model["LOSS"]
    STOP = float(model["STOP"])
    REGULARIZER = model["REGULARIZER"]
    REGULARIZATION_PENALTY = float(model["REGULARIZATION_PENALTY"])
    EPOCHS = int(model["EPOCHS"])
    N_BATCHES = int(model["N_BATCHES"])
    BASE_NAME = str(LEARNING_RATE) + "_" + str(LOSS) + "_" + str(STOP) + "_" + str(REGULARIZER) + "_" + str(REGULARIZATION_PENALTY) + "_" + str(EPOCHS) + "_" + str(N_BATCHES)

    # initialize all the lists required to store the values
    accuracies_val = []
    accuracies_train = []
    accuracies = []
    losses = []
    Y_pred = []
    Y_actual = []

    print("### Beginning n-fold cross validation with parameters: ###")
    print("## Classifier name: {}##".format(BASE_NAME))
    print("## Learning rate:{} ##".format(LEARNING_RATE))
    print("## Epochs:{} ##".format(EPOCHS))
    print("## Regularizer:{} ##".format(REGULARIZER))
    print("## Regularizer penalty:{} ##".format(REGULARIZATION_PENALTY))

    # Create the necessary directories
    if not os.path.isdir("Linear_Classifier/models/"+BASE_NAME):
        os.makedirs("Linear_Classifier/models/"+BASE_NAME)

    if not os.path.isdir("Linear_Classifier/logs/"+BASE_NAME):
        os.makedirs("Linear_Classifier/logs/"+BASE_NAME)

    for i in range(0,n_folds):
        print("## Fold:{} ##".format(i))
        # Begin each training completely separetely

        # Load all the data into the work place
        train_data = np.load(os.path.join("data", "processed", "{}_training.npy".format(i)))
        validation_data = np.load(os.path.join("data", "processed", "{}_validation.npy".format(i)))
        test_data = np.load(os.path.join("data", "processed",  "{}_test.npy".format(i)))

        if test:
            # Join training and validation data for the final test
            train_data = np.concatenate((train_data, validation_data), axis=0)

        # Separete the labels from the features and do one hot encoding for the neural network
        X_train, Y_train = separete_data(train_data)

        if test:
            X_val, Y_val = separete_data(test_data)
        else:
            X_val, Y_val = separete_data(validation_data)

        Y_actual.append(Y_val)

        # Initialize a new classifier per each new fold, all the classifiers are going to have the same parameters
        CLF_NAME = BASE_NAME + "_"+  str(i)
        clf = LinearRegressionClassifier(name = CLF_NAME, base_name = BASE_NAME)

        # Train the classifier
        clf.train(X_train,Y_train,X_val,Y_val,learning_rate = LEARNING_RATE, n_batches = N_BATCHES, epochs=EPOCHS, loss = LOSS, regularizer = REGULARIZER, regularizer_penalty = REGULARIZATION_PENALTY, stop = STOP, save=save, file_path="models")
        clf.visualize()

        # Copy the training accuracy, loss and validation accuracy per fold
        accuracies_val.append(copy.deepcopy(clf.accuracies_val))
        accuracies_train.append(copy.deepcopy(clf.accuracies_train))
        losses.append(copy.deepcopy(clf.losses))

        # Get the validation accracy for one fold
        accuracy = clf.evaluate_model(X_val,Y_val)
        y_pred = clf.predict(X_val)
        Y_pred.append(y_pred)

        if not test:
            # Plot confusion matrix
            plot_confusion_matrix(Y_val, y_pred, BASE_NAME,model="Linear_Classifier", normalize=True, fold=i)
            # and not normalized as well
            plot_confusion_matrix(Y_val, y_pred, BASE_NAME,model="Linear_Classifier", normalize=False, fold=i)

        # Calculate also Recall and precision
        calculate_scores(Y_val, y_pred, BASE_NAME, model="Linear_Classifier", fold=i)

        print("## Validation Accuracy:{} ##".format(accuracy))

        accuracies.append(accuracy)

        # Delete the previous classifier to avoid retraining
        del clf


    # Visualize all folds in one plot
    visualize(accuracies_train, accuracies_val, losses, BASE_NAME)
    if not test:
        print("### Finished n-fold cross validation ###")
    else:
        print("### Finished final test ###")
        Y_actual = np.array(Y_actual).flatten()
        Y_pred = np.array(Y_pred).flatten()
        # Plot confusion matrix
        plot_confusion_matrix(Y_actual, Y_pred, BASE_NAME,model="Linear_Classifier", normalize=True, fold=10)
        # and not normalized as well
        plot_confusion_matrix(Y_actual, Y_pred, BASE_NAME,model="Linear_Classifier", normalize=False, fold=10)
        calculate_scores(Y_val, y_pred, BASE_NAME, model="Linear_Classifier", fold=10)
        mad = calculate_MAD(Y_actual, Y_pred)
        print("## MAD:{} ##".format(mad))

    # Calculate the average accuracy
    final_accuracy = np.mean(np.array(accuracies))
    print("##### Average Accuracy:{} ######".format(final_accuracy))
    return final_accuracy, np.mean(accuracies_train, axis = 0), np.mean(accuracies_val, axis = 0), np.mean(losses, axis = 0)
