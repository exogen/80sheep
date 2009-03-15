Shoes.app do
  background white
  stack do
    border black
    para "Hub name", :align => 'center'
    edit_line :text => "Search!"
    flow do
      stack :width => -150 do
        border black
        para "Notifications"
        stack do
          para "Foo has barred in the baz"
        end
      end
      stack :width => 150 do
        border black
        para "Users"
      end
    end
    edit_box
    edit_line :text => "Chat!"
  end
end
