configuration {
	default: 
		keyword = keyword.control;
		operation = keyword.operator;
	comment:
		line = "//";
		block:
			start = "/*";
			end = "*/";
}

rules {
	keyword:
		Workflow, Init = storage.type;
		Task = entity.name.class;
		Entry, Leave = support.variable;
		Next = storage.modifier;
		Action = storage.modifier;
	operation:
		Task = emphasis;
		Next = storage.type;
}

matches {
	"action" = meta.tag;
}
