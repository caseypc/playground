package org.stefaniuk.args4j.test.parameter;

import org.stefaniuk.args4j.annotation.Argument;
import org.stefaniuk.args4j.annotation.Option;

public class FloatParameters {

    @Argument(index = 0)
    private float argument1;

    @Argument(index = 1)
    private Float argument2;

    @Argument(index = 2)
    private float argument3;

    @Option(name = "/opt1")
    private float option1;

    @Option(name = "/opt2")
    private Float option2;

    @Option(name = "/opt3")
    private Float option3;

    public float getArgument1() {

        return argument1;
    }

    public Float getArgument2() {

        return argument2;
    }

    public float getArgument3() {

        return argument3;
    }

    public float getOption1() {

        return option1;
    }

    public Float getOption2() {

        return option2;
    }

    public Float getOption3() {

        return option3;
    }

}
