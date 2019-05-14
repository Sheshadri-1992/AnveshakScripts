import time

from ProcessEdges import ProducerConsumer

import Rest

my_state = ProducerConsumer()


def initialize_state():
    # Utility/test function call
    my_state.load_json()


if __name__ == '__main__':

    initialize_state()

    rest_app = Rest.create_rest_app(my_state)
    rest_app.run(host='0.0.0.0', port=10001)

    while True:
        time.sleep(1)
