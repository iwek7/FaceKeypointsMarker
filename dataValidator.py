class dataValidator(object):
	"""Class to validate corectness of keypoints dataset"""
	def __init__(self, parent):
		self.parent = parent

		# rules agains which data is validated
		self.validation_rules = dict()
		self.initiate_rules()

	def initiate_rules(self):
		for side in ["RIGHT", "LEFT"]:
			self.validation_rules[side + "_EYE_X"] = (lambda dataline: 
									dataline[side + "_EYE_LEFT"][0] < dataline[side + "_EYE_MIDDLE"][0] < dataline["RIGHT_EYE_RIGHT"][0])

			self.validation_rules[side + "_BROW_X"] = (lambda dataline: 
								dataline[side + "_BROW_LEFT"][0] < dataline[side + "_BROW_RIGHT"][0])
			
			self.validation_rules[side + "_BROW_VS_EYE_Y"] = (lambda dataline:
								(dataline[side + "_BROW_LEFT"][1] < dataline[side + "_EYE_LEFT"][1] and 
										dataline[side + "_BROW_LEFT"][1] < dataline[side + "_EYE_MIDDLE"][1] and
										dataline[side + "_BROW_LEFT"][1] < dataline[side + "_EYE_MIDDLE"][1] and
										dataline[side + "_BROW_RIGHT"][1] < dataline[side + "_EYE_LEFT"][1] and
										dataline[side + "_BROW_RIGHT"][1] < dataline[side + "_EYE_MIDDLE"][1] and
										dataline[side + "_BROW_RIGHT"][1] < dataline[side + "_EYE_MIDDLE"][1])
										)

			self.validation_rules[side + "_EYE_VS_NOSE_Y"] = (lambda dataline:
								(dataline[side + "_EYE_LEFT"][1] < dataline["NOSE"][1] and
										dataline[side + "_EYE_MIDDLE"][1] < dataline["NOSE"][1] and
										dataline[side + "_EYE_RIGHT"][1] < dataline["NOSE"][1]))

		self.validation_rules["EYES_VS_NOSE_X"] = (lambda dataline: 
								dataline["LEFT_EYE_RIGHT"][0] < dataline["NOSE"][0] < dataline["RIGHT_EYE_LEFT"])

		
		self.validation_rules["MOUTH_Y"] = (lambda dataline: 
								dataline["MOUTH_TOP"][1] < dataline["MOUTH_DOWN"][1])
		self.validation_rules["MOUTH_X"] = (lambda dataline :
								(dataline["MOUTH_LEFT"][0] < dataline["MOUTH_TOP"][0] < dataline["MOUTH_RIGHT"][0] and
										dataline["MOUTH_LEFT"][0] < dataline["MOUTH_DOWN"][0] < dataline["MOUTH_RIGHT"][0]))
		self.validation_rules["NOSE_VS_MOUTH_Y"] = (lambda dataline_dict:
								dataline["NOSE"][1] < dataline["MOUTH_LEFT"][1] and
										dataline["NOSE"][1] < dataline["MOUTH_RIGHT"][1] and
										dataline["NOSE"][1] < dataline["MOUTH_TOP"][1])

		def validate_dataset(self):
			errors_stack = list()
			for person in range(self.parent.NUMER_OF_PEOPLE):
				for image in range(self.parent.IMAGES_OF_PERSON):
					self.validate_dataline(self.parent.keypoints_data[person][image],
											errors_stack, image, person)
			return errors_stack

		def validate_dataline(self, dataline, errors_stack, image_num, person_num):
			for rule_name, rule in self.validation_rules.items():
				if not rule(dataline):
					errors_stack.append({"Rule" : rule_nam,
										"Person" : person_num,
										"Image" : image_num})

