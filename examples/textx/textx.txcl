configuration {
	default: 
		keyword = keyword.control;
		operation = keyword.operator.new;
	comment:
		line = "//";
		block:
			start = "/*";
			end = "*/";
}

rules {
	keyword:
		BracketedChoice = constant.character;
}

matches {
	"?=", "*=", "+=" = storage.modifier;
}

regular expressions {
	"\\w+:" = entity.name.class;
}