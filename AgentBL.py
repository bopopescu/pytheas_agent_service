import numpy as np

class AgentServiceBL:

    def __init__(self):
        # self.date_importer = DataImporter();
        self.a = 1

    def calculate_user_tags_matrix(self, data_set):
        n_users = len(data_set)
        n_items = len(data_set.columns)
        print('')
        print('User Tags Data:')
        print(str(n_users) + ' users')
        print('')

        data_set_matrix = data_set.reset_index().values
        matrix = np.zeros((n_users, n_items))

        for i in range(0, n_users):
            for j in range(1, n_items):
                matrix[i, j - 1] = data_set_matrix[i, j]

        sparsity = float(len(matrix.nonzero()[0]))
        shapes = (matrix.shape[0] * matrix.shape[1]);
        if (shapes != 0):
            sparsity /= shapes
        else:
            sparsity = 0
        sparsity *= 100

        print('Sparsity: {:4.2f}%'.format(sparsity))
        return matrix

    def calculate_user_ratings_matrix(self, data_set, attractions_list):
        n_users = len(data_set)
        n_items = len(attractions_list)
        n_max_rev_for_user = len(data_set.columns) - 2
        print(str(n_users) + ' users')

        rating_matrix = np.zeros((n_users, n_items))
        for name, user_ratings in data_set.iterrows():
            i = 0
            while ((i < n_max_rev_for_user) & (user_ratings[i] != None)):
                column_index = attractions_list.index(user_ratings[i][0])
                if ((column_index > -1) & (column_index < n_items)):
                    rating_matrix[user_ratings["_ID"], column_index] = user_ratings[i][1]
                i += 1

        sparsity = float(len(rating_matrix.nonzero()[0]))
        shapes = (rating_matrix.shape[0] * rating_matrix.shape[1]);
        if (shapes != 0):
            sparsity /= shapes
        else:
            sparsity = 0
        sparsity *= 100

        print('Sparsity: {:4.2f}%'.format(sparsity))
        return rating_matrix

    def center_matrix(self, matrix):
        mean_point = []
        for row in range(len(matrix)):
            row_count = 0
            row_sum = 0
            row_avg = 0
            for cell in range(len(matrix[0])):
                if matrix[row][cell] != 0:
                    row_count = row_count + 1
                    row_sum = row_sum + matrix[row][cell]
            if (row_count != 0): row_avg = row_sum / row_count
            mean_point.append(row_avg)

        # subtract mean point
        centered_matrix = matrix.copy()  # - meanPoint

        for row in range(len(mean_point)):
            for cell in range(len(centered_matrix[0])):
                if centered_matrix[row][cell] != 0:
                    centered_matrix[row][cell] -= mean_point[row]
        return centered_matrix, mean_point

    def fast_similarity(self, matrix, kind='user', epsilon=1e-9):
        # epsilon -> small number for handling dived-by-zero errors
        sim = 1
        if (kind == 'user'):
            sim = matrix.dot(matrix.T) + epsilon
        elif kind == 'item':
            sim = matrix.T.dot(matrix) + epsilon
        norms = np.array([np.sqrt(np.diagonal(sim))])
        return (sim / (norms / norms.T))

    def predict1(self, original_matrix, similarity_matrix, mean_point, type='user'):
        if type == 'user':
            mean_user_rating = original_matrix.mean(axis=1)
            # We use np.newaxis so that mean_user_rating has same format as ratings
            ratings_diff = (original_matrix - mean_user_rating[:, np.newaxis])
            # print('hey')
            ratings_diff = original_matrix;
            prediction = mean_user_rating[:, np.newaxis] + similarity_matrix.dot(ratings_diff) / np.array(
                [np.abs(similarity_matrix).sum(axis=1)]).T
        elif type == 'item':
            prediction = original_matrix.dot(similarity_matrix) / np.array([np.abs(similarity_matrix).sum(axis=1)])

        # print (pred);

        for row in range(len(prediction)):
            for cell in range(len(prediction[0])):
                prediction[row][cell] += mean_point[row]

        return prediction

    def predict(self, original_matrix, similarity, meanPoint, type='user'):

        if type == 'user':
            mean_user_rating = original_matrix.mean(axis=1)
            # We use np.newaxis so that mean_user_rating has same format as ratings
            ratings_diff = (original_matrix - mean_user_rating[:, np.newaxis])
            # print('hey')
            ratings_diff = original_matrix;
            pred = mean_user_rating[:, np.newaxis] + similarity.dot(ratings_diff) / np.array(
                [np.abs(similarity).sum(axis=1)]).T
        elif type == 'item':
            pred = original_matrix.dot(similarity) / np.array([np.abs(similarity).sum(axis=1)])

        # print (pred);

        for row in range(len(pred)):
            for cell in range(len(pred[0])):
                pred[row][cell] += meanPoint[row]

        return pred

    def calculate_error_rate(self, orgiginal_matrix, prediction_matrix):
        count_elements = 0
        sum_error_gap = 0
        count_success = 0
        cost = 0
        error_rate = 0
        for i in range(len(orgiginal_matrix)):
            for j in range(len(orgiginal_matrix[0])):
                cell = orgiginal_matrix[i][j]
                predictCell = round(prediction_matrix[i][j])

                if (cell != 0):
                    count_elements += 1
                    if (cell - predictCell >= 0):
                        sum_error_gap += cell - predictCell
                    else:
                        sum_error_gap -= cell - predictCell

                    if (cell == predictCell): count_success += 1;
        cost = sum_error_gap * sum_error_gap;
        error_rate = cost / count_elements;
        print('')
        print('count Elements: {:4.2f}'.format(count_elements))
        print('sumErrorGap: {:4.2f}'.format(sum_error_gap))
        print('Count Success: {:4.2f}'.format(count_success))
        print('')
        print('Cost: {:4.2f}'.format(cost))
        print('Precent Success: {:4.2f}'.format(100 - (error_rate)))
        print('Precent Error: {:4.2f}'.format((error_rate)))
        return;



