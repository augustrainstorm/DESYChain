#!/usr/bin/env python
# coding: utf-8

# In[2]:


class Cluster:
    def __init__(self, pixels_list):
        self.x = 0
        self.y = 0
        self.pixels_list = pixels_list
        
    def calc_center(self):
        sum_x = 0
        sum_y = 0
        for (i,j) in self.pixels_list:
            sum_x += i
            sum_y += j
            
        self.x = sum_x / len(self.pixels_list)
        self.y = sum_y / len(self.pixels_list)
        
        return (self.x, self.y)
    
    def print(self):
        print(self.pixels_list)
    
    def add(self, pixel):
        self.pixels_list.append(pixel)
            


# In[7]:


class ClusterAlgorithm:
    def __init__(self, pixels_list):
        self.pixels_list = pixels_list
        
    def calc_clusters(self):
        cluster_list = []
        
        pixels_to_check = list(self.pixels_list)
        
        for pixel in self.pixels_list:
            #Remove current pixel from pixels_to_check list in order to compare all other pixels
            if pixel in pixels_to_check:
                pixels_to_check.remove(pixel)
            else:
                continue
            
            #Determine if current pixel can fit into existing cluster
            #If so, return the cluster
            found_cluster, cluster = self.has_cluster(cluster_list, pixel)
            
            if found_cluster:
                #Add pixel to existing cluster
                cluster_list[cluster_list.index(cluster)].add(pixel)
            else:
                #Create new cluster from pixel
                c = Cluster([pixel])
                for pixel_unchecked in pixels_to_check:
                    #Add remaining pixels to cluster if they are direct neighbors with current pixel
                    if self.are_neighbors(pixel_unchecked, pixel):
                        c.add(pixel_unchecked)
                        pixels_to_check.remove(pixel_unchecked)
                cluster_list.append(c)
        
        for cluster in cluster_list:
            cluster.print()
        
        return cluster_list
         
    def are_neighbors(self, pixel1, pixel2):
        if abs(pixel1[0] - pixel2[0]) <= 1 and abs(pixel1[1] - pixel2[1]) <= 1:
            return True
        else:
            return False
            
    def has_cluster(self, cluster_list, pixel):
        for cluster in cluster_list:
            for p in cluster.pixels_list:
                if self.are_neighbors(pixel, p):
                    return True, cluster
        return False, None
            


# In[8]:


pixels_list = [(1,1), (2,1), (3,1), (4,1), (5,1), (2,2), (6,5), (6,6), (7,6), (7,5), (8,5), (10, 10)]
cluster_algo = ClusterAlgorithm(pixels_list)


# In[9]:


f = cluster_algo.calc_clusters()


# In[10]:


for cluster in f:
    print(cluster.calc_center())


# In[ ]:




