package net.rootmode.admin.test;

import static org.junit.Assert.assertTrue;

import net.rootmode.admin.SampleClass;

import org.junit.After;
import org.junit.AfterClass;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;

public class SampleTest {

    @BeforeClass
    public static void setUpClass() throws Exception {

        // Code executed before the first test method
    }

    @Before
    public void setUp() throws Exception {

        // Code executed before each test
    }

    @Test
    public void testSomething() {

        // Code that tests one thing

        SampleClass sc = new SampleClass("Hello World!");
        sc.setSampleField("This is a test.");
        assertTrue("This is a test.".equals(sc.getSampleField()));
    }

    @After
    public void tearDown() throws Exception {

        // Code executed after each test
    }

    @AfterClass
    public static void tearDownClass() throws Exception {

        // Code executed after the last test method
    }

}
