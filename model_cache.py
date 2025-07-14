from qiskit_ibm_runtime import QiskitRuntimeService
from qiskit_aer.noise import NoiseModel
import pickle

def ibm_account_connect(token, instance):
    try:
        QiskitRuntimeService.save_account(
        token=token,
        channel="ibm_cloud", # `channel` distinguishes between different account types.
        instance=instance, # Copy the instance CRN from the Instance section on the dashboard.
        name="ibm_qc_credential", # Optionally name this set of credentials.
        overwrite=True # Only needed if you already have Cloud credentials.
        )
        print("Account Created - Continuing.")
    except:
        print("Account Exists - Continuing.")
    return None

def cache_noise_model(backend_name, filename):
    """
    Cache the noise model from a given IBM backend.
    
    Parameters:
    - backend_name: str, e.g., "ibm_torino"
    - filename: str, e.g., "cached_noise_model.pkl"
    - instance_name: str, IBM Quantum instance name
    """
    
    service = QiskitRuntimeService(name = "ibm_qc_credential")  # corrected key
    backend = service.backend(backend_name)

    noise_model = NoiseModel.from_backend(backend)

    with open(filename, "wb") as f:
        pickle.dump(noise_model, f)

    print(f"\t -> Noise model from {backend_name} saved to {filename}")

def update_quantum_models(token, instance):
    ibm_account_connect(token, instance)
    devices = {
        "ibm_torino": "heron_model.pkl",
        "ibm_brisbane": "eagle_brisbane_model.pkl",
        "ibm_sherbrooke": "eagle_sherbrooke_model.pkl"
    }

    for backend_name, file_name in devices.items():
        cache_noise_model(backend_name, file_name)


token = input("Enter your token: ")
instance = input("Enter your CRN: ")
    

update_quantum_models(token, instance)
