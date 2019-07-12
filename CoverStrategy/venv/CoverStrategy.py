# SHIFT strategy example

from shift_engine import subscribe, info, get_product_traits, start_timer, kill_timer, send_IOC, prepare_trading
from shift_engine import STRATEGY_TIMER_STEP_US
from shift_utils import ObjectFromDict
from random import randint, choice
from math import isnan


class StrategyState(object):
    def __init__(self):
        self.product_name = 'ntprog.USD/RUB'
        self.features = ['BidPx', 'AskPx', 'MidPx']
        self.product_traits = ObjectFromDict(get_product_traits(self.product_name))
        self.available_order_count = 0
        self.sent_count = 0
        self.mdspecid = None
        self.on_order_available_timer_id = None


class StrategyCtx(object):

    def __init__(self):
        self.state = StrategyState()

    def dump_strategy(self):
        strategy_dump = []
        for member in dir(self.params):
            if not member.startswith('_'):
                strategy_dump.append('params.{}: {}'.format(member, getattr(self.params, member)))
        for member in dir(self.state):
            if not member.startswith('_'):
                strategy_dump.append('state.{}: {}'.format(member, getattr(self.state, member)))
        info('Strategy dump: {}'.format(', '.join(strategy_dump)))

    def on_params(self):
        if self.state.mdspecid is None:
            self.state.mdspecid = subscribe(self.state.product_traits.id, self.state.features)
            prepare_trading(self.state.product_traits.id)

        if self.state.on_order_available_timer_id is not None:
            if self.params.verbose:
                info('Killing existing timer {}'.format(self.state.on_order_available_timer_id))
            kill_timer(self.state.on_order_available_timer_id)
            self.state.on_order_available_timer_id = None

        if self.params.one_order_per_interval:
            self.state.on_order_available_timer_id = start_timer(int(self.params.one_order_per_interval))

        if self.params.verbose:
            traits_dump = []
            for member in dir(self.state.product_traits):
                if not member.startswith('_'):
                    traits_dump.append('{}: {}'.format(member, getattr(self.state.product_traits, member)))
            info('Product traits: {}'.format(', '.join(traits_dump)))

        info('Python cover strategy was successfully initialized with parameters: {}'.format(self.params))

    def on_order_status(self, now_us, status):
        if self.params.verbose:
            info('OrderStatus={} at {}, position {}'.format(status, now_us, self.risk.current_position))

    def on_md(self, now_us, mdspecid, features):
        if mdspecid != self.state.mdspecid:
            raise Exception('Invalid market data update received. Should be {}, received {}'.format(
                self.state.mdspecid, mdspecid))

        if self.params.verbose:
            info('Received USD/RUB data: ts={}, bidpx={}, askpx={}, midpx={}'.format(
                now_us, features[0], features[1], features[2]))

        if self.state.available_order_count > self.state.sent_count:
            buy = self.params.is_buy
            amount = self.params.cover_amount
            if not amount:
                return
            # send aggressive order
            limit_price = features[1 if buy else 0]
            if isnan(limit_price):
                return
            if self.params.verbose:
                info('Sending IOC for USD/RUB data: buy={}, amount={}, limit_price={}, tag={}'.format(
                    buy, amount, limit_price, self.state.sent_count))
            send_IOC(self.state.product_traits.id, buy, amount, limit_price, self.state.sent_count)
            self.state.sent_count += 1


def on_params(ctx):
    ctx.on_params()


def on_md(ctx, now_us, mdspecid, features):
    ctx.on_md(now_us, mdspecid, features)


def on_order_status(ctx, now_us, status):
    ctx.on_order_status(now_us, status)


def on_timer(ctx, now_us, timer_id):
    if timer_id != ctx.state.on_order_available_timer_id:
        raise Exception('Invalid timer id received {}'.format(timer_id))
    ctx.state.available_order_count += 1


class Strategy:
    """
    Class definition to register the strategy
    """
    ctx_type = StrategyCtx
    default_params = {
        'max_orders_per_min': 10,
        'pos_limit': 1000000,
        'verbose': False    #??? - ask Chris
    }

    callbacks = {
        'on_params': on_params,
        'on_md': on_md,
        'on_order_status': on_order_status,
        'on_timer': on_timer
    }
