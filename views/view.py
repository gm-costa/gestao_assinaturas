import __init__
from datetime import date, datetime
import matplotlib.pyplot as plt
from sqlmodel import Session, select
from models.model import Payment, Subscription


class SubscriptionService:
    def __init__(self, engine):
        self.engine = engine

    def create(self, subscription: Subscription):
        with Session(self.engine) as session:
            session.add(subscription)
            session.commit()
            session.refresh(subscription)
            return subscription
        
    def list_all(self):
        with Session(self.engine) as session:
            statement = select(Subscription)
            results = session.exec(statement).all()
        return results

    def get_one(self, choice):
        with Session(self.engine) as session:
            statement = select(Subscription).where(Subscription.id==choice)
            result = session.exec(statement).one()

        return result
    
    def delete(self, id_subscription):
        with Session(self.engine) as session:
            statement = select(Subscription).where(Subscription.id==id_subscription)
            result = session.exec(statement).one()
            session.delete(result)
            session.commit()
    
    def _has_pay(self, results):
        for result in results:
            if result.date.month == date.today().month:
                return True
        return False

    def pay(self, id_subscription):
        with Session(self.engine) as session:
            statement = select(Payment).join(Subscription).where(Subscription.id==id_subscription)
            results = session.exec(statement).all()

            if self._has_pay(results):
                return False
                
            pay = Payment(
                subscription_id=id_subscription,
                date=date.today()
            )
            session.add(pay)
            session.commit()

        return True
        
    def list_all_pays(self):
        with Session(self.engine) as session:
            statement = select(Payment, Subscription).join(Subscription)
            results = session.exec(statement).all()

        return results
    
    def list_all_pays_from_subscription(self, choice):
        with Session(self.engine) as session:
            statement = select(Payment).where(Payment.subscription_id==choice)
            results = session.exec(statement).all()

        return results

    def delete_pay(self, choice):
        with Session(self.engine) as session:
            statement = select(Payment).where(Payment.id==choice)
            result = session.exec(statement).one()
            session.delete(result)
            session.commit()

    def total_value(self):
        with Session(self.engine) as session:
            statement = select(Subscription)      
            results = session.exec(statement).all()

        total = 0
        for result in results:
            total += result.valor

        return float(total)

    def _get_last_12_months_native(self):
        today = datetime.now()
        year = today.year
        month = today.month
        last_12_months = []
        for _ in range(12):
            last_12_months.append((month, year))
            month -= 1
            if month == 0:
                month = 12
                year -= 1
        return last_12_months[::-1]

    def _get_values_for_months(self, last_12_months):
        with Session(self.engine) as session:
            statement = select(Payment)
            results = session.exec(statement).all()

            value_for_months = []
            for i in last_12_months:
                value = 0
                for result in results:
                    if result.date.month == i[0] and result.date.year == i[1]:
                        value += float(result.subscription.valor)

                value_for_months.append(value)
        return value_for_months

    def gen_chart(self):
        last_12_months = self._get_last_12_months_native()
        values_for_months = self._get_values_for_months(last_12_months)
        last_12_months = list(map(lambda x: str(x[0])+'/'+str(x[1])[2:], self._get_last_12_months_native()))

        plt.plot(last_12_months, values_for_months)
        plt.show()