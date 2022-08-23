from chessboard_location.deps import *


def draw_intersections_on_image(img, intersections):

    if intersections is None:
        return img
        
    img_result = img.copy()

    intersections = np.apply_along_axis(lambda x: tuple(reversed(x)), 2, intersections)

    for i, row in enumerate(intersections):
        for j, intersection in enumerate(row):
            if not (j < len(row) - 1):
                continue
            if i == 0 or i == len(intersections) - 1:
                cv2.line(img_result, intersection, row[j + 1], color=(0,0, 255), thickness=3)
            else:
                cv2.line(img_result, intersection, row[j + 1], color=(0,0, 200), thickness=2)

    intersections_T = intersections.transpose([1, 0, 2])

    for i, row in enumerate(intersections_T):
        for j, intersection in enumerate(row):
            if not (j < len(row) - 1):
                continue
            if i == 0 or i == len(intersections) - 1:
                cv2.line(img_result, intersection, row[j + 1], color=(0,0, 255), thickness=3)
            else:
                cv2.line(img_result, intersection, row[j + 1], color=(0,0, 200), thickness=2)

    for i, row in enumerate(intersections):
        for j, intersection in enumerate(row):
            cv2.circle(img_result, intersection, radius=5, color=(75, 200, 0), thickness=-1)
    
    return img_result

def draw_line_on_image(img, line, color, thickness=1): 
    rho = line[0]
    theta = line[1]

    a = math.cos(theta)
    b = math.sin(theta)
    x0, y0 = a*rho, b*rho
    pt1 = ( int(x0+2000*(-b)), int(y0+2000*(a)) )
    pt2 = ( int(x0-2000*(-b)), int(y0-2000*(a)) )
    
    cv2.line(img, pt1, pt2, color, thickness, cv2.LINE_AA)

def draw_lines_cluster(img, lines, color=(0, 0, 255)):
    img_result = img.copy()
    for line in lines:
        draw_line_on_image(img_result, line, color, 1)
    return img_result

def draw_lines_labeled(img, lines, labels):

    colorArray = np.random.randint(255, size = max(labels + 1))

    for i, line in enumerate(lines):
        if labels[i] == -1:
            color = (0, 0, 0)
        else:
            color = colorArray[labels[i]]

        draw_line_on_image(img, line, color, 1)

def plot_clusters(lines, labels):
    plt.scatter([line[0] for line in lines], [line[1] for line in lines], c = labels, cmap= "plasma") # plotting the clusters
    plt.xlabel("Y-Axis") # X-axis label
    plt.ylabel("X-Axis") # Y-axis label
    plt.show() # showing the plot

def resize_image(img, height=600):
    pixels = height * height
    shape = list(img.shape)
    scale = math.sqrt(float(pixels)/float(shape[0]*shape[1]))
    
    shape[0] *= scale; shape[1] *= scale
    img = cv2.resize(img, (int(shape[1]), int(shape[0])))
    return img