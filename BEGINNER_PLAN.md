# Beginner-Friendly Guide for Linking Doctors to Patients Using Python Dictionaries and Lists

## Introduction
In this guide, you will learn how to link doctors to patients using Python data structures such as dictionaries and lists. We will take you step-by-step through the process, providing clear examples and explanations along the way.

## Step 1: Understand the Data Structure
In our example, we will use a dictionary to represent doctors, where each doctor has a unique ID and their details (like name and specialization). We will also use a list to hold the patients, where each patient will have a reference to the doctor treating them.

### Example Structure
```python
# Doctor data structure
 doctors = {
    1: {'name': 'Dr. John Smith', 'specialization': 'Cardiology'},
    2: {'name': 'Dr. Jane Doe', 'specialization': 'Pediatrics'},
}

# Patients list
patients = [
    {'name': 'Alice', 'doctor_id': 1},
    {'name': 'Bob', 'doctor_id': 2},
]
```

## Step 2: Linking Patients to Doctors
To link patients to their respective doctors, we can create a simple function that takes a patient name and returns the doctor's details.

### Code Example
```python
def get_doctor_info(patient_name):
    for patient in patients:
        if patient['name'] == patient_name:
            doctor_id = patient['doctor_id']
            return doctors.get(doctor_id, 'Doctor not found')
    return 'Patient not found'
```

### Explanation
In the above code:
- We define a function `get_doctor_info()` that looks for a patient in the `patients` list.
- If the patient is found, it retrieves the `doctor_id` and uses it to fetch the doctor's details from the `doctors` dictionary.
- If either the patient or doctor is not found, it returns a message accordingly.

## Step 3: Example Usage
You can now use the function to fetch the doctor information for any patient.

### Code Example
```python
# Example usage
patient_name = 'Alice'
doctor_info = get_doctor_info(patient_name)
print(f'{patient_name} is linked to {doctor_info}')
```

## Conclusion
You have learned how to link doctors to patients using Python dictionaries and lists. This beginner-friendly guide provides a foundational understanding that you can build upon as you advance in your programming journey.

Happy coding!