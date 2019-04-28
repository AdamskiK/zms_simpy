# -*- coding: utf-8 -*-
"""
Created on Wed Apr  5 14:51:36 2017

@author: team X
"""

import simpy
import numpy as np

AVG_WORKING_TIME = 75  # average working time without a single failure
AVG_REPAIR_TIME = 15  # an average fix time


def time_to_failure(avg_working_time=AVG_WORKING_TIME):
    """Calculate a failure probability while given an average working time

    :param avg_working_time: average work-time without a single failure
    :type avg_working_time: integer
    :return: a probability
    :rtype: float
    """
    return np.random.exponential(avg_working_time)


def repair_time(avg_repair_time=AVG_REPAIR_TIME):
    """Draw samples from a Gamma distribution

    :param avg_repair_time: a repair time
    :type avg_repair_time: integer
    :return: Drawn samples from the parameterized gamma distribution.
    :rtype: ndarray or scalar
    """
    return np.random.gamma(3, avg_repair_time/3)


def machine(env, machine_id, repairman, setup, broken_time_cum):
    """Define a simulation model

    :param env: a simulation environment
    :type env: simpy.core.Environment object
    :param machine_id: machine id
    :type machine_id: integer
    :param repairman: a resource
    :type repairman: simpy.core.Resource object
    :param setup: a conveyor type - a linear "L" or star "G" type
    :type setup: string
    :param broken_time_cum:
    :type broken_time_cum:
    :return: timeout
    :rtype: Timeout object
    """
    while True:
        if setup == "L":
            tools_delivery = 2*(machine_id + 1)  # a repair time
        elif setup == "G":
            tools_delivery = 3
        else:
            print("A wrong setup type")
            break

        yield env.timeout(time_to_failure())  # wait until a machine failure
        broken = env.now  # record a failure time
        print('Machine %d broke at time of %d' % (machine_id, broken))

        with repairman.request() as req:  # send a request for a machine repair
            yield req
            yield env.timeout(tools_delivery)
            wait = env.now - broken
            print('A machine %d has been waiting %d for tools, the repair has started at %d' \
                  % (machine_id, wait, env.now))
            yield env.timeout(repair_time())
            print('The machine %d has been repaired at %d' % (machine_id, env.now))
            broken_time = env.now - broken
            broken_time_cum[machine_id] += broken_time
            yield env.timeout(tools_delivery)


def run_model(tools, machines, setup, horizon):
    """Run a single simulation

    :param tools: a number of tool packages
    :type tools: integer
    :param machines: a number of machines
    :type machines: integer
    :param setup: a conveyor type - a linear "L" or star "G" type
    :type setup: string
    :param horizon: a horizon time
    :type horizon: integer
    :return: cumulative time of broken machines
    :rtype: list
    """
    env = simpy.Environment()  # create an environment
    repairman = simpy.Resource(env, capacity=tools)  # create a resource
    broken_time_cum = [0] * machines  # create a list which will keep a broken time per machine
    for i in range(machines):  # create n machines
        env.process(machine(env, i, repairman, setup, broken_time_cum))
    env.run(until=horizon * 24 * 60)
    return broken_time_cum


def run_simulation(iterations, tools, machines, setup, horizon):
    """Run simulation function

    :param iterations: a number of iterations
    :type iterations:  integer
    :param tools: a number of tool packages
    :type tools: integer
    :param machines: a number of machines
    :type machines: integer
    :param setup: a conveyor type - a linear "L" or star "G" type
    :type setup: string
    :param horizon: a horizon time
    :type horizon: integer
    :return: cumulative time of broken machines
    :rtype: list
    """
    broken_time_cum = []
    for i in range(iterations):
        run = run_model(tools, machines, setup, horizon)
        broken_time_cum.append(run)
    return list(map(np.mean, np.transpose(broken_time_cum)))


def main():
    results = run_simulation(iterations=1, tools=1, machines=6, setup="L", horizon=30)
    print(f"final results: {results}")


if __name__ == '__main__':
    main()
