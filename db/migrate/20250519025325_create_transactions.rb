class CreateTransactions < ActiveRecord::Migration[7.2]
  def change
    create_table :transactions do |t|
      t.integer :num_transaction
      t.integer :day
      t.integer :hour
      t.integer :money #definir si va a ser integer o double o qué
      t.string :desc 
      t.string :motive

      t.timestamps
    end
  end
end
