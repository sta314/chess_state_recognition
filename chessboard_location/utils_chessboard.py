from chessboard_location.deps import *

# Reference : CannyLines paper - parameterless canny edge algorithm 
def cannyPF(img, sigma=0.25):
    med = np.median(img)
    lower = int(max(0, (1.0 - sigma) * med))
    upper = int(min(255, (1.0 + sigma) * med))
    return cv2.Canny(img, lower, upper)

# Reference : https://stackoverflow.com/a/383527
def intersection(line1, line2, img_shape): 
    rho1, theta1 = line1
    rho2, theta2 = line2
    A = np.array([
        [np.cos(theta1), np.sin(theta1)],
        [np.cos(theta2), np.sin(theta2)]
    ])
    b = np.array([[rho1], [rho2]])
    try:
        x0, y0 = np.linalg.solve(A, b)
    except:
        x0, y0 = (-1, -1)
    x0, y0 = int(np.round(x0)), int(np.round(y0))
    if abs(y0) > img_shape[0] * chessboard_location.params.parallel_threshold or abs(x0) > img_shape[0] * chessboard_location.params.parallel_threshold:
        x0, y0 = (-1, -1)
    return [y0, x0]

def fix_hessian_form(line, reverse=False):
    if not reverse and line[0] < 0:
        new_rho = - (line[0])
        new_alpha = -(np.pi - line[1])
        return (new_rho, new_alpha)
    elif reverse and line[1] < 0:
        new_rho = - (line[0])
        new_alpha = np.pi + line[1]
        return (new_rho, new_alpha)
    return line

def fix_hessian_form_vectorized(lines):
    lines = lines.copy()
    neg_rho_mask = lines[:, 0] < 0
    lines[neg_rho_mask, 0] *= -1
    lines[neg_rho_mask, 1] -= np.pi

    return lines 

def angle_diff(line1, line2):
    diff = float('inf')
    if (line1[0] < 0) ^ (line2[0] < 0):
        if line1[0] < 0:
            diff = abs(fix_hessian_form(line1)[1] - line2[1]) % (np.pi)
        else:
            diff = abs(line1[1] - fix_hessian_form(line2)[1]) % (np.pi)

    diff = min(diff, abs(line1[1] - line2[1]) % (np.pi))

    return diff 

def angle_diff_vectorized(lines, line_to_calculate_diff):
    hess_fixed_lines = fix_hessian_form_vectorized(lines)
    hess_fixed_calculate_line = fix_hessian_form(line_to_calculate_diff)

    diff_fixed = np.full(lines.shape[0], float('inf'))
    hess_test_mask = lines[:, 0] < 0
    
    if line_to_calculate_diff[0] >= 0:
        diff_fixed[hess_test_mask] = np.mod(np.abs(hess_fixed_lines[hess_test_mask, 1] - line_to_calculate_diff[1]), np.pi)
    else:
        diff_fixed[~hess_test_mask] = np.mod(lines[~hess_test_mask, 1] - hess_fixed_calculate_line[1], np.pi)
    
    diff_normal = np.mod(np.abs(lines[:, 1] - line_to_calculate_diff[1]), np.pi)

    return np.minimum(diff_normal, diff_fixed)

def cluster_mean_hessfixed(lines, cluster):
    
    cluster_lines = lines[list(cluster)]
    normal_mean = np.mean(cluster_lines, axis=0)

    hess_fixed_cluster_lines = fix_hessian_form_vectorized(cluster_lines)
    hess_fixed_mean = np.mean(hess_fixed_cluster_lines, axis=0)

    normal_mean_diff = np.mean(angle_diff_vectorized(cluster_lines, normal_mean))
    hess_fixed_mean_diff = np.mean(angle_diff_vectorized(cluster_lines, hess_fixed_mean))

    return (normal_mean if normal_mean_diff < hess_fixed_mean_diff else fix_hessian_form(hess_fixed_mean, True)) 

def split_clusters_using_labels(all_clusters, labels):
    cluster_list = []

    for cluster_id in range(max(labels) + 1):
        mask = (labels == cluster_id)
        cluster_list.append(np.array(all_clusters)[mask])

    return cluster_list