import numpy as np


class BusinessLogic:

    @staticmethod
    def predict_knn(original_matrix, similarity, mean_point, type='user'):

        if type == 'user':
            mean_user_rating = original_matrix.mean(axis=1)
            ratings_diff = original_matrix
            prediction = mean_user_rating[:, np.newaxis] + similarity.dot(ratings_diff) / np.array(
                [np.abs(similarity).sum(axis=1)]).T
        elif type == 'item':
            prediction = original_matrix.dot(similarity) / np.array([np.abs(similarity).sum(axis=1)])
        for row in range(len(prediction)):
            for cell in range(len(prediction[0])):
                prediction[row][cell] += mean_point[row]

        return prediction

    @staticmethod
    def predict_mf(original_matrix, similarity, mean_point, type='user'):

        if type == 'user':
            mean_user_rating = original_matrix.mean(axis=1)
            ratings_diff = original_matrix;
            prediction = mean_user_rating[:, np.newaxis] + similarity.dot(ratings_diff) / np.array(
                [np.abs(similarity).sum(axis=1)]).T
        elif type == 'item':
            prediction = original_matrix.dot(similarity) / np.array([np.abs(similarity).sum(axis=1)])

        for row in range(len(prediction)):
            for cell in range(len(prediction[0])):
                prediction[row][cell] += mean_point[row]

        return prediction

    @staticmethod
    def calculate_error_rate(original_matrix, prediction_matrix):
        count_elements = 0
        sum_error_gap = 0
        count_success = 0
        cost = 0
        error_rate = 0
        for i in range(len(original_matrix)):
            for j in range(len(original_matrix[0])):
                cell = original_matrix[i][j]
                predict_cell = round(prediction_matrix[i][j])

                if cell != 0:
                    count_elements += 1
                    if cell - predict_cell >= 0:
                        sum_error_gap += cell - predict_cell
                    else:
                        sum_error_gap -= cell - predict_cell

                    if cell == predict_cell:
                        count_success += 1
        cost = sum_error_gap * sum_error_gap
        error_rate = cost / count_elements
        return cost, error_rate

    @staticmethod
    def calculate_user_tags_matrix(data_set):
        n_users = len(data_set)
        n_items = len(data_set.columns)

        data_set_matrix = data_set.reset_index().values
        matrix = np.zeros((n_users, n_items))

        for i in range(0, n_users):
            for j in range(1, n_items):
                matrix[i, j - 1] = data_set_matrix[i, j]

        sparsity = float(len(matrix.nonzero()[0]))
        shapes = (matrix.shape[0] * matrix.shape[1])
        if shapes != 0:
            sparsity /= shapes
        else:
            sparsity = 0
        sparsity *= 100

        return matrix

    @staticmethod
    def calculate_user_ratings_matrix(data_set, attractions_list):
        n_users = len(data_set)
        n_items = len(attractions_list)
        n_max_rev_for_user = len(data_set.columns) - 2

        rating_matrix = np.zeros((n_users, n_items))
        for name, user_ratings in data_set.iterrows():
            i = 0
            while i < n_max_rev_for_user and user_ratings[i] is not None:
                column_index = attractions_list.index(user_ratings[i][0])
                if column_index > -1 and column_index < n_items:
                    rating_matrix[user_ratings["_ID"], column_index] = user_ratings[i][1]
                i += 1
        sparsity = float(len(rating_matrix.nonzero()[0]))
        shapes = (rating_matrix.shape[0] * rating_matrix.shape[1])
        if shapes != 0:
            sparsity /= shapes
        else:
            sparsity = 0
        sparsity *= 100

        return rating_matrix, sparsity

    @staticmethod
    def center_matrix(matrix):
        mean_point = []
        for row in range(len(matrix)):
            row_count = 0
            row_sum = 0
            row_avg = 0
            for cell in range(len(matrix[0])):
                if matrix[row][cell] != 0:
                    row_count = row_count + 1
                    row_sum = row_sum + matrix[row][cell]
            if row_count != 0:
                row_avg = row_sum / row_count
            mean_point.append(row_avg)
        centered_matrix = matrix.copy()

        for row in range(len(mean_point)):
            for cell in range(len(centered_matrix[0])):
                if centered_matrix[row][cell] != 0:
                    centered_matrix[row][cell] -= mean_point[row]
        return centered_matrix, mean_point

    @staticmethod
    def fast_similarity(matrix, kind='user', epsilon=1e-9):
        # epsilon -> small number for handling dived-by-zero errors
        sim = 1
        if kind == 'user':
            sim = matrix.dot(matrix.T) + epsilon
        elif kind == 'item':
            sim = matrix.T.dot(matrix) + epsilon
        norms = np.array([np.sqrt(np.diagonal(sim))])
        return sim / (norms / norms.T)

    @staticmethod
    def matrix_factorization(r, p, q, k, steps=6, alpha=0.007, beta=0.5):
        for step in range(steps):
            for i in range(len(r)):
                for j in range(len(r[i])):
                    if r[i][j] > 0:
                        eij = r[i][j] - np.dot(p[i, :], q[:, j])
                        for x in range(k):
                            p[i][x] = p[i][x] + alpha * (2 * eij * q[x][j] - beta * p[i][x])
                            q[x][j] = q[x][j] + alpha * (2 * eij * p[i][x] - beta * q[x][j])
        return p, q.T

    @staticmethod
    def round_matrix(matrix):
        result_matrix = matrix.copy()
        for row in range(len(matrix)):
            for cell in range(len(matrix[0])):
                result_matrix[row][cell] = round(result_matrix[row][cell])
                if result_matrix[row][cell] > 5:
                    result_matrix[row][cell] = 5
                if result_matrix[row][cell] < 0:
                    result_matrix[row][cell] = 1
        return result_matrix

    @staticmethod
    def union_prediction_matrixes(first_matrix, second_matrix):
        n_rows = len(first_matrix)
        n_columns = len(first_matrix[0])
        if len(first_matrix) > len(second_matrix):
            n_rows = len(second_matrix)
        if len(first_matrix[0]) > len(second_matrix[0]):
            n_columns = len(second_matrix[0])

        for i in range(n_rows):
            for j in range(n_columns):
                if round(first_matrix[i][j]) == 0 and round(second_matrix[i][j]) != 0:
                    first_matrix[i][j] = round(second_matrix[i][j])
        return first_matrix




