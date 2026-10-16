import sys
import argparse
from CalcRating import CalcRating
#from TextDataReader import TextDataReader as Reader
from XmlDataReader import XmlDataReader as Reader
from StudentFiltering import StudentFiltering as Filter



def get_path_from_arguments(args) -> str:
    parser = argparse.ArgumentParser(description="Path to datafile")
    parser.add_argument("-p", dest="path", type=str, required=True, help="Path to datafile")
    args = parser.parse_args(args)
    return args.path

def main():
    path = get_path_from_arguments(sys.argv[1:])
    reader = Reader()
    students = reader.read(path)
    print("Students:")
    for student, grades in students.items():
        print(f"{student}")
        for name, value in grades:
            print(f"\t{name}: {value}")

    rating = CalcRating(students).calc()
    print("Rating: ")
    for name, value in rating.items():
        print(f"\t{name}: {value}")

    print("Filter >= 76: ")
    for name, value in Filter(lambda _, x: x >= 76).filter(rating).items():
        print(f"\t{name}: {value}")


if __name__ == "__main__":
    main()
