def adicionar_tarefa():
    tarefa = input("Digite a tarefa a ser adicionada: ")
    with open("tarefas.txt", "a") as arquivo:
        arquivo.write(tarefa + "\n")
    print("Tarefa adicionada com sucesso!")


def exibir_tarefas():
    with open("tarefas.txt", "r") as arquivo:
        tarefas = arquivo.readlines()
    if len(tarefas) == 0:
        print("Não há tarefas a serem exibidas.")
    else:
        for i, tarefa in enumerate(tarefas):
            print(f"{i+1}. {tarefa.strip()}")


def editar_tarefa():
    with open("tarefas.txt", "r") as arquivo:
        tarefas = arquivo.readlines()
    if len(tarefas) == 0:
        print("Não há tarefas a serem editadas.")
    else:
        exibir_tarefas()
        numero_tarefa = int(input("Digite o número da tarefa a ser editada: "))
        if numero_tarefa <= 0 or numero_tarefa > len(tarefas):
            print("Número inválido.")
        else:
            nova_tarefa = input("Digite a nova tarefa: ")
            tarefas[numero_tarefa - 1] = nova_tarefa + "\n"
            with open("tarefas.txt", "w") as arquivo:
                arquivo.writelines(tarefas)
            print("Tarefa editada com sucesso!")


def excluir_tarefa():
    with open("tarefas.txt", "r") as arquivo:
        tarefas = arquivo.readlines()
    if len(tarefas) == 0:
        print("Não há tarefas a serem excluídas.")
    else:
        exibir_tarefas()
        numero_tarefa = int(input("Digite o número da tarefa a ser excluída: "))
        if numero_tarefa <= 0 or numero_tarefa > len(tarefas):
            print("Número inválido.")
        else:
            tarefas.pop(numero_tarefa - 1)
            with open("tarefas.txt", "w") as arquivo:
                arquivo.writelines(tarefas)
            print("Tarefa excluída com sucesso!")


while True:
    print("\n--- GERENCIADOR DE TAREFAS ---")
    print("1. Adicionar tarefa")
    print("2. Exibir tarefas")
    print("3. Editar tarefa")
    print("4. Excluir tarefa")
    print("5. Sair")
    opcao = input("Digite a opção desejada: ")
    if opcao == "1":
        adicionar_tarefa()
    elif opcao == "2":
        exibir_tarefas()
    elif opcao == "3":
        editar_tarefa()
    elif opcao == "4":
        excluir_tarefa()
    elif opcao == "5":
        print("Saindo do programa...")
        break
    else:
        print("Opção inválida.")
