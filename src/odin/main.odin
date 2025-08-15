package main

import "core:fmt"
import "core:os"


print :: proc(value: $T) {
	fmt.printf("\nTyp: %T \nVal: %v\n", value, value)
    //fmt.println(typeid_of(type_of(value)))
    //fmt.println(type_info_of(typeid_of(type_of(value))))
}


Globo :: struct {
	ncols : int,
	nrows : int,
}
//v := Globo{32, 32}
//v
//fmt.println(v.NCOLS)


Generation :: struct {
	using globo: Globo,
	curr_state : matrix[1,1]int
}

Cell :: struct {
}



create_globo :: proc(dim: int) -> (globo: Globo) {
	//globo.ncols 
	return globo
}

print_globo :: proc(state: matrix) -> {

	

}

/*
	Vector2 :: struct {
		x: f32,
		y: f32,
	}
	v := Vector2{1, 2}
	v.x = 4
	fmt.println(v.x)
*/

main :: proc() {

	globo := create_globo(32)
	print(globo)

	gen := Generation{
		globo,

	}


	print(gen)

	// -------------------------
	/*FOR 
	for i := 0; i < 10; i += 1 {
		print(i)
	}
	// equals 
	for i in 0..<10 {
		print(i)
	}
	// or
	for i in 0..=9 do print(i)
	// while
	//for do print("Hellope!")
	*/
	// -------------------------

	/*
	print("Hellope!")

	b := matrix[16, 1]f32{}
	fmt.println("b", b)
	
	f := f32(3)
	// b = f
	fmt.println("f", f)
	//fmt.println("b == f", b == f)


	y: int // `y` is typed of type `int`
	y = 1  // `1` is an untyped integer literal which can implicitly convert to `int`

	if len(os.args) > 2 {

	}

	// constants
	NC : int : 16
	NR : int : 32


	z: f64 // `z` is typed of type `f64` (64-bit floating point number)
	z = 1 
	*/

}


