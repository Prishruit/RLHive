from hive.utils.registry import registry
from hive.agents.qnets.atari import NatureAtariDQNModel
from hive.agents.qnets.base import FunctionApproximator
from hive.agents.qnets.conv import ConvNetwork
from hive.agents.qnets.mlp import MLPNetwork
from hive.agents.qnets.rnn import ConvRNNNetwork

registry.register_all(
    FunctionApproximator,
    {
        "MLPNetwork": FunctionApproximator(MLPNetwork),
        "ConvNetwork": FunctionApproximator(ConvNetwork),
        "ConvRNNNetwork": FunctionApproximator(ConvRNNNetwork),
        "NatureAtariDQNModel": FunctionApproximator(NatureAtariDQNModel),
    },
)

get_qnet = getattr(registry, f"get_{FunctionApproximator.type_name()}")
