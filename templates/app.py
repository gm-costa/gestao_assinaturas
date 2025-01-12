import __init__
import os
from models.model import Subscription
from views.view import SubscriptionService
from models.database import engine
from datetime import datetime
from decimal import Decimal
from rich.table import Table
from rich.console import Console


console = Console()

def clear_screen():
    input('\nTecle <ENTER> para continuar ...')
    os.system('clear') or None

def colorir(texto, cor=37, bold=0, end='\n'):
    print(f"\033[{bold};{cor}m{texto}\033[0m", end=end)


class UI:
    def __init__(self):
        self.subscription_service = SubscriptionService(engine)

    def add_subscription(self):
        while True:
            print('-' * 50)
            empresa = input('Empresa: ')
            site = input('Site: ')
            data_assinatura = datetime.strptime(input('Data de assinatura: '), '%d/%m/%Y')
            valor = Decimal(input('Valor: '))

            subscription = Subscription(empresa=empresa, site=site, data_assinatura=data_assinatura, valor=valor)
            self.subscription_service.create(subscription)
            colorir('\nAssinatura adicionada com sucesso.', 32)
            print('-' * 50)

            choice = input('Adicionar outra? [s/N]: ').upper()[:1] or 'N'

            match choice:
                case 'N':
                    break
                case 'S':
                    continue
                case _:
                    colorir('Opção inválida!', 31)
                    break

    def list_subscriptions(self, subscriptions):
        table = Table(title='Lista de Assinaturas')
        headers = ['id', 'empresa', 'valor']
        for header in headers:
            table.add_column(header, style='green')
        for x in subscriptions:
            x.valor = f'{x.valor:.2f}'
            values = [str(getattr(x, header)) for header in headers]
            table.add_row(*values)

        print()
        console.print(table)
    
    def delete_subscription(self):
        subscriptions = self.subscription_service.list_all()
        self.list_subscriptions(subscriptions)

        choice = int(input('\nInforme o ID da assinatura que deseja excluir: '))

        try:
            self.subscription_service.delete(choice)
            colorir('\nAssinatura excluída com sucesso, inclusive seus pagamentos.', 32)
        except:
            colorir('\nID não presente na lista!', 33)

        print('-' * 50)

    def pay_subscription(self):
        subscriptions = self.subscription_service.list_all()
        self.list_subscriptions(subscriptions)

        choice = int(input('\nInforme o ID da assinatura que deseja efetuar o pagamento: '))

        try:
            subscription = self.subscription_service.get_one(choice)
            if self.subscription_service.pay(choice):
                colorir('\nAssinatura paga com sucesso.', 32)
            else:
                colorir('\nA assinatura deste mês já foi paga.', 33)
        except:
            colorir('\nID não presente na lista!', 33)

        print('-' * 50)

    def list_payments(self):
        subscriptions = self.subscription_service.list_all()
        self.list_subscriptions(subscriptions)

        choice = int(input('\nInforme o ID da assinatura que deseja listar os pagamentos: '))

        try:
            subscription = self.subscription_service.get_one(choice)
            payments = self.subscription_service.list_all_pays_from_subscription(choice)
            if payments:
                title = f'Pagamentos {subscription.empresa}'
                valor = f'{subscription.valor:.2f}'
                table = Table(title=title)
                headers = ['ID', 'DATA', 'VALOR']
                for header in headers:
                    table.add_column(header, style='green')
                for pay in payments:
                    values = [str(pay.id), datetime.strftime(pay.date, '%d/%m/%Y'), valor]
                    table.add_row(*values)
                print()
                console.print(table)
            else:
                colorir('\nNão existe pagamentos para esta assinatura.', 36)

        except:
            colorir('\nID não presente na lista!', 33)

    def delete_payment(self):
        payments = self.subscription_service.list_all_pays()
        if payments:
            table = Table(title='Lista de todos os pagamentos')
            headers = ['ID', 'EMPRESA', 'DATA', 'VALOR']
            for header in headers:
                table.add_column(header, style='green')
            for pay, subscription in payments:
                values = [
                    str(pay.id), 
                    subscription.empresa,
                    datetime.strftime(pay.date, '%d/%m/%Y'), 
                    f'{subscription.valor:.2f}'
                ]
                table.add_row(*values)
                
            print()
            console.print(table)

            choice = int(input('\nInforme o ID do pagamento que deseja excluir: '))

            try:
                self.subscription_service.delete_pay(choice)
                colorir('\nPagamento excluído com sucesso.', 32)
            except:
                colorir('\nID não presente na lista!', 33)

        else:
            colorir('\nNão há pagamento cadastrado!', 33)
        
        print('-' * 50)

    def total_value(self):
        print('-' * 50)
        colorir('Seu valor total mensal em assinaturas: ', cor=32, end='')
        colorir(f'R$ {self.subscription_service.total_value():.2f}', 36)
        print('-' * 50)

    def start(self):
        while True:
            print('''
            ------------------------------
                         MENU
            ------------------------------
            [1] -> Adicionar assinatura
            [2] -> Listar assinaturas
            [3] -> Remover assinatura
            [4] -> Pagar assinatura
            [5] -> Listar pagamentos por assinatura
            [6] -> Remover pagamento
            [7] -> Valor total
            [8] -> Gastos últimos 12 meses
            [9] -> Sair
            ''')

            choice = int(input('Escolha uma opção: '))

            if choice == 1:
                self.add_subscription()
            elif choice == 2:
                subscriptions = self.subscription_service.list_all()
                self.list_subscriptions(subscriptions)
            elif choice == 3:
                self.delete_subscription()
            elif choice == 4:
                self.pay_subscription()
            elif choice == 5:
                self.list_payments()
            elif choice == 6:
                self.delete_payment()
            elif choice == 7:
                self.total_value()
            elif choice == 8:
                self.subscription_service.gen_chart()
            elif choice == 9:
                break
            else:
                colorir('\n\tOpção inválida !', 31)

            clear_screen()


if __name__ == '__main__':
    UI().start()
