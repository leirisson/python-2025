from classes_entidades.Estudante import Estudante


def main():
    
    nome = input("Qual o nome doe estudante: ")
    idade = int(input("Qual a idade do estudante: "))
    matricula = input("Qual a matricula: ")
    leirisson_estudante = Estudante(nome, idade, matricula)

    print(leirisson_estudante.apresentar())

if __name__ == "__main__":
    main()