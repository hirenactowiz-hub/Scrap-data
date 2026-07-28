def part_of_chunks(input_list,size):
    result = []
    
    for i in range(0, len(input_list), size):
        print(i)
        chunk = input_list[i : i + size]
        print(chunk)
        
        result.append(chunk)
    return result
my_list = list(range(1,13))
print(part_of_chunks(my_list,5))




