from classes.Cachorro import Cachorro
from classes.Gato import Gato




def main():
    cachorro_rex = Cachorro("Rex")
    gato_luna = Gato("Luna")
    
    print(cachorro_rex.fazer_som())
    print(gato_luna.fazer_som())

if __name__ == "__main__":
    main()