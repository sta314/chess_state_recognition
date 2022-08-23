line_amount = 200 # amount of best lines selected from hough lines 
bilateral_filter_size = 7 # size of the bilateral filter for noise removal


parallel_threshold = 64 # intersections of 2 lines occured on distance > {}*image_size is assumed as parallel
parallel_angle_threshold = 0.04 # merge two parallel line clusters if angle difference is < {} (in radians)
two_line_cluster_threshold = 1.0 # angle difference between two line clusters of chess table should be < {} (in radians)


dbscan_eps_intersection_clustering = 10
dbscan_eps_duplicate_elimination = 3

polynomial_degree = 3 # used for fitting polynomial to intersection data, last step of the pipeline