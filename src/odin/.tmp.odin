package tmp

import "core:fmt"


print :: proc(value: $T) {
	fmt.printf("T: %T \nV: %v\n", value, value)
    //fmt.println(typeid_of(type_of(value)))
    //fmt.println(type_info_of(typeid_of(type_of(value))))
}


main :: proc() {

    mat: matrix[2,2]f32
    
    print(mat)

}