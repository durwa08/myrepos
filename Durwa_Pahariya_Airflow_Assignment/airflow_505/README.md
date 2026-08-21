import logging
import random
from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.bash import BashOperator

# Setup task logger
log = logging.getLogger("airflow.task")

# Survival thresholds
AMMO_THRESHOLD = 15
THREAT_THRESHOLD = 7

def check_perimeter(**context):
    """
    Scouts the perimeter and rates zombie activity on a scale of 1-10.
    Pushes the threat rating to XCom.
    """
    log.info("Starting perimeter scan.")
    threat = random.randint(1, 10)
    
    if threat >= THREAT_THRESHOLD:
        log.warning(f"High threat detected: {threat}/10!")
    else:
        log.info(f"Perimeter clear. Threat level: {threat}/10.")
        
    context['ti'].xcom_push(key='threat_level', value=threat)

def check_ammo(**context):
    """
    Counts available ammunition rounds in the armory.
    Pushes the total to XCom.
    """
    log.info("Counting remaining ammunition.")
    ammo = random.randint(5, 50)
    
    if ammo < AMMO_THRESHOLD:
        log.critical(f"Low ammo warning! Only {ammo} rounds left.")
    else:
        log.info(f"Ammo count stable: {ammo} rounds.")
        
    context['ti'].xcom_push(key='ammo_count', value=ammo)

def make_decision(**context):
    """
    Evaluates threat and ammo to choose the next action.
    If threat is high and ammo is low, it triggers a lockdown.
    Otherwise, the team fights and reinforces the base.
    """
    ti = context['ti']
    threat = ti.xcom_pull(task_ids='check_perimeter', key='threat_level')
    ammo = ti.xcom_pull(task_ids='check_ammo', key='ammo_count')
    
    log.info(f"Analyzing situation -> Threat: {threat}, Ammo: {ammo}")
    
    if threat >= THREAT_THRESHOLD and ammo < AMMO_THRESHOLD:
        log.error("Threat too high for current ammo. Ordering immediate lockdown.")
        return 'lockdown_bunker'
    else:
        log.info("Conditions acceptable. Proceeding to reinforce base.")
        return 'reinforce_base'

def reinforce_base():
    """Secures windows and fortifies active entry points."""
    log.info("Sealing windows and reinforcing structural barriers.")

def lockdown_bunker():
    """Kills power and goes completely silent to hide."""
    log.warning("Killing all lights. Initiating total audio silence.")

def radio_broadcast(**context):
    """Sends a shortwave status update to other survivor camps."""
    log.info("Broadcasting secure status update over shortwave radio.")

# Define the DAG
with DAG(
    dag_id='zombie_survival_dag',
    schedule_interval='0 18 * * *', # Runs every day at 18:00 (6:00 PM) dusk lockdown
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=['survival'],
) as dag:

    # 1. Check Perimeter (Python)
    t1 = PythonOperator(
        task_id='check_perimeter',
        python_callable=check_perimeter,
    )

    # 2. Check Ammo (Python)
    t2 = PythonOperator(
        task_id='check_ammo',
        python_callable=check_ammo,
    )

    # 3. Decision Branch (Branching Python)
    t3 = BranchPythonOperator(
        task_id='make_decision',
        python_callable=make_decision,
    )

    # 4. Action Branch A (Python)
    t4 = PythonOperator(
        task_id='reinforce_base',
        python_callable=reinforce_base,
    )

    # 5. Action Branch B (Python)
    t5 = PythonOperator(
        task_id='lockdown_bunker',
        python_callable=lockdown_bunker,
    )

    # 6. Check Generator (Bash)
    t6 = BashOperator(
        task_id='check_generator',
        bash_command='echo "[$(date)] Checking backup diesel generator fuel levels..."',
    )

    # 7. Radio Broadcast (Python) - Rejoins the two branches
    t7 = PythonOperator(
        task_id='radio_broadcast',
        python_callable=radio_broadcast,
        trigger_rule='one_success',
    )

    # 8. Close Log (Bash)
    t8 = BashOperator(
        task_id='close_log',
        bash_command='echo "[$(date)] Dusk lockdown routine complete. Secure for the night."',
    )

    # Pipeline execution flow (8 tasks total)
    [t1, t2] >> t3
    t3 >> t4 >> t7
    t3 >> t5 >> t7
    
    t6 >> t8
    t7 >> t8
