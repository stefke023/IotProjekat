
.PHONY: help central_controller devices



help:
	@echo "Make help for python project"
	@echo "First step: run make devices on one computer"
	@echo "Second step: run make central_controller on a computer with MQQT broker installed."

central_controller: 
	@echo "Running central controller"
	@powershell -Command "wt -w 0 new-tab --startingDirectory . cmd /k 'cd .\CentralController && python central_control.py'"


devices: 
	@echo "Running devices.."
	@powershell -Command "wt -w 0 new-tab --startingDirectory . cmd /k 'cd .\Subscriber && python ventilation_actuator.py'"
	@powershell -Command "wt -w 0 new-tab --startingDirectory . cmd /k 'cd .\Subscriber && python alarm_actuator.py'"
	@powershell -Command "wt -w 0 new-tab --startingDirectory . cmd /k 'cd .\Subscriber && python gui_aplication.py'"
	@powershell -Command "wt -w 0 new-tab --startingDirectory . cmd /k 'cd .\Devices && python server.py'"
	@powershell -Command "wt -w 0 new-tab --startingDirectory . cmd /k 'cd .\Publisher && python dust_sensor.py'"
	@powershell -Command "wt -w 0 new-tab --startingDirectory . cmd /k 'cd .\Publisher && python gas_sensor.py'"

