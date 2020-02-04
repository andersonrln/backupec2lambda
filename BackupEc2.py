import boto3
from datetime import datetime

def backup():
    date_format = "%d/%m/%Y"
    date_time_format = "%d/%m/%Y_%H_%M_%S"
    created_by_value = "lambda-backup-script"

    start_time = datetime.now()

    # inicializado o ec2 client
    ec2_client = boto3.client('ec2')

    regions = ec2_client.describe_regions()

    for region in regions['Regions']:
        print("Regiao: " + str(region['RegionName']))
        ec2_client = boto3.client('ec2', region_name=region['RegionName'])
        instances = ec2_client.describe_instances()
        for reservation in instances['Reservations']:
            for instance in reservation['Instances']:
                
                #ignorando instancias com estados invalidos...
                if instance['State']['Name'] == "running" \
                        or instance['State']['Name'] == "stopping" \
                            or instance['State']['Name'] == "stopped":
                    date_time = datetime.now().strftime(date_time_format)
                    date = datetime.now().strftime(date_format)
                    ami_name = "backup_by_lambda__" + instance['InstanceId'] + "__" +  date_time
                    ami_desc = ami_name
                    print "Fazendo backup da instancia: " + \
                        instance['InstanceId'] + " >> " + ami_desc
                    ami_id = ec2_client.create_image(InstanceId=instance['InstanceId'], \
                                                     Name=ami_name, Description=ami_desc, \
                                                     NoReboot=True)
                    ec2_client.create_tags(Resources=[ami_id['ImageId']], \
                                           Tags=[{'Key': 'creation_date','Value': date}, \
                                                 {'Key': 'created_by', \
                                                    'Value': created_by_value}])
    
    end_time = datetime.now()
    took_time = end_time - start_time
    print "Tempo total de execucao: " + str(took_time)    

def lambda_handler(event, context):
    print('Iniciando backup... ')
    backup()