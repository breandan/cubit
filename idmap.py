
class IdMap(object):
	''' fake lm when a real lm is not avail'''
	@staticmethod
	def words2indices(s):
		from qstr import QStr
		return QStr(tuple(s))
	
	@staticmethod
	def ppqstr(s):
		return " ".join(s)

	@staticmethod
	def pq(s):
		return 0, IdMap.words2indices(s)

	@staticmethod
	def stopsyms():
		return ("</s>", )

	@staticmethod
	def clear():
		pass
