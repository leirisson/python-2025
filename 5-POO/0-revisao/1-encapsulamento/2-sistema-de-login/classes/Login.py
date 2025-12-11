class Login:
    def __init__(self, nome, senha):
        self.nome = nome
        self.__senha = senha # Senha é privada
        
        
    def validar_senha(self, senha_digitada) -> bool:
        as_senhas_sao_iguais: bool = (self.__senha == senha_digitada)
        return as_senhas_sao_iguais
    
    
    def alterar_senha(self, senha_antiga:str, nova_senha:str):
        if self.validar_senha(senha_antiga):
            self.__senha = nova_senha
            return "Senha alterada com sucesso."
        return "Senha antiga incorreta."
    
    