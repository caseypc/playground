package com.code4ge.args4j.tests.options;

import com.code4ge.args4j.annotations.Argument;
import com.code4ge.args4j.annotations.Option;

public class ByteOptions {

	@Argument(index = 0)
	private byte argument1;

	@Argument(index = 1)
	private Byte argument2;

	@Argument(index = 2)
	private byte argument3;

	@Option(name = "/opt1")
	private byte option1;

	@Option(name = "/opt2")
	private Byte option2;

	@Option(name = "/opt3")
	private Byte option3;

	public byte getArgument1() {

		return argument1;
	}

	public Byte getArgument2() {

		return argument2;
	}

	public byte getArgument3() {

		return argument3;
	}

	public byte getOption1() {

		return option1;
	}

	public Byte getOption2() {

		return option2;
	}

	public Byte getOption3() {

		return option3;
	}

}
