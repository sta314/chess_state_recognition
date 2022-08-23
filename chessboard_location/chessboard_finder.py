from chessboard_location.deps import *
from chessboard_location.utils_chessboard import *
import chessboard_location.params

def get_chessboard_intersections(img, debug = False):
    
    try:
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

        gray_filtered = cv2.bilateralFilter(gray, chessboard_location.params.bilateral_filter_size, 75, 75)

        edges = cannyPF(gray_filtered)

        lines = cv2.HoughLines(edges, 1, np.pi/720.0, 50, np.array([]), 0, 0)
        lines_best = np.squeeze(lines)[:chessboard_location.params.line_amount]

        intersections, intersections_info, parallel_sets_list = __get_all_line_intersections(lines_best, gray.shape)

        intersecting_clusters = __get_intersecting_line_clusters(intersections, intersections_info)
        parallel_clusters = __get_parallel_line_clusters(lines_best, parallel_sets_list)

        best_cluster_pair = __select_best_performing_cluster_pair(lines_best, intersecting_clusters, parallel_clusters)

        cluster_means = [cluster_mean_hessfixed(lines_best, best_cluster_pair[0]), cluster_mean_hessfixed(lines_best, best_cluster_pair[1])]

        best_cluster_pair_duplicate_eliminated = [__cluster_eliminate_duplicate(lines_best, best_cluster_pair[0], cluster_means[1], img.shape), __cluster_eliminate_duplicate(lines_best, best_cluster_pair[1], cluster_means[0], img.shape)]
        
        best_cluster_pair_chessboard = __cluster_eliminate_non_chessboard(best_cluster_pair_duplicate_eliminated, cluster_means, img.shape)

        all_corners_in_chessboard = __get_intersections_between_clusters(best_cluster_pair_chessboard[0], best_cluster_pair_chessboard[1], img.shape)
    except:
        all_corners_in_chessboard = None
        return all_corners_in_chessboard

    if not debug:
        return all_corners_in_chessboard
    if debug:
        return all_corners_in_chessboard, gray, gray_filtered, edges, lines_best, best_cluster_pair, best_cluster_pair_duplicate_eliminated, best_cluster_pair_chessboard

def __get_all_line_intersections(lines, img_shape): # can vectorize intersection calculations later on
    parallel_sets_list = list()
    intersections_info = list()
    intersections = list()
    for i, line in enumerate(lines):
        for j, line in enumerate(lines[i:], start = i):
            if i == j:
                continue
            line_intersection = intersection(lines[i], lines[j], img_shape)
            if line_intersection[0] == -1 and line_intersection[1] == -1:
                set_exists = False
                for next_set in parallel_sets_list:
                    if (i in next_set) or (j in next_set):
                        set_exists = True   
                        next_set.add(i)
                        next_set.add(j)
                        break
                if not set_exists:
                    parallel_sets_list.append({i, j})
            else:
                if not ((0 < line_intersection[0] < img_shape[0]) and (0 < line_intersection[1] < img_shape[1])): # Ignoring intersections within visible image
                    intersections_info.append((i, j))
                    intersections.append(line_intersection)
    return intersections, intersections_info, sorted(parallel_sets_list, key=len, reverse=True)

def __get_intersecting_line_clusters(intersections, intersections_info):
    dbscan_intersections = DBSCAN(eps = chessboard_location.params.dbscan_eps_intersection_clustering, min_samples = 8).fit(intersections) # 10, 8
    labels_intersections = dbscan_intersections.labels_

    intersection_clusters = split_clusters_using_labels(intersections_info, labels_intersections)

    unique_lines_each_cluster = list()
    for cluster in intersection_clusters:
        unique_lines = set()
        for lines in cluster:
            unique_lines.add(lines[0])
            unique_lines.add(lines[1])
        unique_lines_each_cluster.append(unique_lines)

    return sorted(unique_lines_each_cluster, key=len, reverse=True)

def __get_parallel_line_clusters(lines, parallel_sets):
    cur_sets = parallel_sets
    cur_means = list()
    for next_set in cur_sets:
        cur_means.append(np.mean(lines[list(next_set)], axis=0)[1])
    
    i = 0
    while i < (len(cur_sets) - 1):
        for j in range(i + 1, len(cur_sets)):
            if abs(cur_means[i] - cur_means[j]) < chessboard_location.params.parallel_angle_threshold:
                cur_sets[i] = cur_sets[i] | cur_sets[j]
                cur_means[i] = np.mean(lines[list(cur_sets[i])], axis=0)[1]
                cur_sets.pop(j)
                cur_means.pop(j)
                i = 0
                break
        i += 1
    return sorted(cur_sets, key=len, reverse=True)

def __select_best_performing_cluster_pair(lines, intersections, parallel_sets):

    merged_clusters = intersections + parallel_sets
    merged_sizes = list(map(lambda x: len(x), merged_clusters))

    pass_list = list()
    for i, cluster_i in enumerate(merged_clusters):
        for j, cluster_j in enumerate(merged_clusters[i:], start=i):
            if i == j:
                continue
            if(angle_diff(cluster_mean_hessfixed(lines, cluster_i), cluster_mean_hessfixed(lines, cluster_j)) > chessboard_location.params.two_line_cluster_threshold):
                pass_list.append((i, j))

    pass_list.sort(key = lambda x: (merged_sizes[x[0]] * merged_sizes[x[1]]), reverse=True)
    winner_pair = pass_list[0]

    return (merged_clusters[winner_pair[0]], merged_clusters[winner_pair[1]])

def __cluster_eliminate_duplicate(lines, cluster, intersect_line, img_shape):
    cluster_lines = lines[list(cluster)]
    intersection_points = list(map(lambda x: intersection(x, intersect_line, img_shape), cluster_lines))

    dbscan_test = DBSCAN(eps = chessboard_location.params.dbscan_eps_duplicate_elimination, min_samples = 1).fit(intersection_points)
    labels_test = dbscan_test.labels_

    merged_cluster = list()
    for i in range(max(labels_test) + 1):
        mask = (labels_test == i)
        merged_cluster.append(cluster_mean_hessfixed(lines, np.array(list(cluster))[mask]))

    return merged_cluster

def __cluster_eliminate_non_chessboard(merged_clusters, cluster_means, img_shape):

    first_cluster, second_cluster = merged_clusters

    mean_first_cluster, mean_second_cluster = cluster_means

    intersections_first_cluster = list(map(lambda x: intersection(x, mean_second_cluster, img_shape), first_cluster))

    intersections_second_cluster = list(map(lambda x: intersection(x, mean_first_cluster, img_shape), second_cluster))        


    
    best_intersections_first_cluster = __select_nine_fittable_intersections(intersections_first_cluster)
    best_intersections_second_cluster = __select_nine_fittable_intersections(intersections_second_cluster)
    

    return (np.array(first_cluster)[best_intersections_first_cluster], np.array(second_cluster)[best_intersections_second_cluster])

def __select_nine_fittable_intersections(intersections):

    np_intersections = np.array(intersections)
    
    axis_variance = np.var(np_intersections, axis=0)

    metric_col = (0 if axis_variance[0] > axis_variance[1] else 1)
    metric_value = np_intersections[:, metric_col]

    sorted_idx = np.argsort(metric_value)
    metric_value = metric_value[sorted_idx]

    all_combinations_iter = itertools.combinations(np.array(list(enumerate(metric_value))), 9)
    all_combinations = np.stack(np.fromiter(all_combinations_iter, dtype=(tuple)))

    x = range(9)
    fitter = lambda y: np.poly1d(np.polyfit(x, y, chessboard_location.params.polynomial_degree))(x)
    all_combinations_fitted_calculated = np.apply_along_axis(fitter, 1, all_combinations[:, :, 1])

    all_combinations_mse = (np.square(all_combinations[:, :, 1] - all_combinations_fitted_calculated)).mean(axis=1)

    best_combination_indexes = all_combinations[np.argmin(all_combinations_mse)][:, 0]

    sorted_idx_reverse_dict = {k: v for k, v in enumerate(sorted_idx)}

    best_combination_indexes_reversed = [sorted_idx_reverse_dict[k] for k in best_combination_indexes]

    return best_combination_indexes_reversed

def __get_intersections_between_clusters(cluster1, cluster2, img_shape):
    intersections = np.empty((len(cluster1), len(cluster2), 2),dtype=np.int32)
    for i, line_1 in enumerate(cluster1):
        for j, line_2 in enumerate(cluster2):
            intersections[i][j] = intersection(line_1, line_2, img_shape)
    return intersections
