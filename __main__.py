from simplex.Tableau import *

if __name__ == "__main__":
    tableau = Tableau([Product('x1', 4, s1=1, s2=7, s3=3),
                       Product('x2', 5, s1=1, s2=5, s3=5),
                       Product('x3', 9, s1=1, s2=3, s3=10),
                       Product('x4', 11, s1=2, s2=3, s3=5)],
                      {'s1': 15, 's2': 120, 's3': 100})
    for version in tableau:
        print (version)
