

class Produto:
    def __init__(self, nome: str, preco: float, quantida_estoque: int) -> None:
        self.nome = nome
        self.preco = preco
        self.quantidade_estoque = quantida_estoque
        
    def adicionar(self, qtd_produto: int) -> str:
        if(qtd_produto <=0):
            raise Exception(f"Não pode inserir no estoque a quantidade de produto igual há: {qtd_produto}")
        self.quantidade_estoque += qtd_produto
        return f"Quantidade: {qtd_produto} de produtos adicionada com sucesso."
    
    def remover(self, qtd_produto: int) -> str:
        if(qtd_produto > self.quantidade_estoque):
            raise Exception(f"Não pode remover uma quantidade maior do que a que está no estoque.")
        self.quantidade_estoque -= qtd_produto
        return f"Baixa em {qtd_produto} realizada com sucesso."
    
    def calcular_valor_estoque(self) -> str:
        valor_total_estoque = self.preco * self.quantidade_estoque
        return f"valor totoal do estoque é: {valor_total_estoque}"
    
    def estoque_atual(self) -> str:
        return f"nome: {self.nome} | preço: {self.preco} | estoque: {self.quantidade_estoque}"